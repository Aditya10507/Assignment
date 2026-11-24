// ============================================================
// PART 1 — LOAD DATA ON PAGE LOAD
// ============================================================

let allResults = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchResults();
});

async function fetchResults() {
    try {
        // Fetch the saved JSON data from the backend
        const response = await fetch('/api/results');
        allResults = await response.json();
        renderTable();
    } catch (error) {
        document.getElementById('tableBody').innerHTML = 
            `<tr><td colspan="5" style="color:red;">Failed to load data. Make sure the backend is running.</td></tr>`;
    }
}

// ============================================================
// PART 2 — DRAW THE TABLE
// ============================================================

function renderTable() {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    if (allResults.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5">No results found. Run generate_all.py first.</td></tr>`;
        return;
    }

    allResults.forEach(result => {
        const conceptId = result.concept.id;
        
        // Check localStorage for any saved approval/rejection
        const saved = JSON.parse(localStorage.getItem(`review_${conceptId}`)) || { status: 'PENDING', note: '' };

        const tr = document.createElement('tr');
        
        // 1. Concept Column
        tr.innerHTML += `
            <td>
                <strong>${result.concept.name}</strong><br>
                <small style="color: #6B7280;">${result.concept.subject}</small>
            </td>`;

        // 2. Diagram Column
        let svgHtml = result.svg ? result.svg : `<span style="color:red; font-size:12px;">API Error / No SVG</span>`;
        tr.innerHTML += `
            <td>
                <div class="svg-container">${svgHtml}</div>
            </td>`;

        // 3. Checks Column
        let checksHtml = '';
        if (result.checks) {
            const badgeClass = result.all_passed ? 'status-pass' : 'status-fail';
            const badgeText = result.all_passed ? 'PASSED' : 'FAILED';
            checksHtml = `<div class="status-badge ${badgeClass}">${badgeText}</div><ul class="check-list">`;
            
            for (const [name, passed] of Object.entries(result.checks)) {
                checksHtml += `<li class="${passed ? 'check-pass' : 'check-fail'}">
                    ${passed ? '✓' : '✗'} ${name}
                </li>`;
            }
            checksHtml += '</ul>';
        } else {
            checksHtml = `<span style="color:red; font-size:12px;">${result.api_error || 'Failed'}</span>`;
        }
        tr.innerHTML += `<td>${checksHtml}</td>`;

        // 4. Metrics Column
        tr.innerHTML += `
            <td>
                <div class="metrics"><strong>Model:</strong> ${result.model || 'N/A'}</div>
                <div class="metrics"><strong>Cost:</strong> $${result.cost_usd || '0.00'}</div>
                <div class="metrics"><strong>Retries:</strong> ${result.retries || 0}</div>
            </td>`;

        // 5. Actions Column (Approve, Reject, Generate)
        tr.innerHTML += `
            <td>
                <div class="actions-column">
                    <div class="button-group">
                        <button class="btn-approve" onclick="saveReview(${conceptId}, 'APPROVED')">Approve</button>
                        <button class="btn-reject" onclick="saveReview(${conceptId}, 'REJECTED')">Reject</button>
                    </div>
                    <div id="status-text-${conceptId}" style="font-weight:bold; font-size:12px; color: ${saved.status === 'APPROVED' ? 'var(--success)' : saved.status === 'REJECTED' ? 'var(--error)' : '#666'}">
                        Status: ${saved.status}
                    </div>
                    <textarea id="note-${conceptId}" placeholder="Reviewer notes...">${saved.note}</textarea>
                    <button class="btn-generate" id="btn-gen-${conceptId}" onclick="generateLive(${conceptId})">Re-Generate Live</button>
                </div>
            </td>`;

        tbody.appendChild(tr);
    });
}

// ============================================================
// PART 3 — ACTIONS (Save Approve/Reject & Generate)
// ============================================================

function saveReview(conceptId, status) {
    const note = document.getElementById(`note-${conceptId}`).value;
    
    // Save to browser's localStorage so it survives a refresh
    localStorage.setItem(`review_${conceptId}`, JSON.stringify({ status: status, note: note }));
    
    // Update the UI immediately
    const statusText = document.getElementById(`status-text-${conceptId}`);
    statusText.innerText = `Status: ${status}`;
    statusText.style.color = status === 'APPROVED' ? 'var(--success)' : 'var(--error)';
}

async function generateLive(conceptId) {
    const btn = document.getElementById(`btn-gen-${conceptId}`);
    const originalText = btn.innerText;
    
    // Show loading state
    btn.innerText = "Generating... (Wait ~5s)";
    btn.disabled = true;

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ concept_id: conceptId })
        });

        if (!response.ok) {
            // If FastAPI throws a 500 error (like the API failed), show it
            const errorData = await response.json();
            throw new Error(errorData.detail || "Failed to generate");
        }

        const newResult = await response.json();
        
        // Update our local array with the new result
        const index = allResults.findIndex(r => r.concept.id === conceptId);
        allResults[index] = newResult;
        
        // Redraw the table to show the new SVG
        renderTable();

    } catch (error) {
        // Show a clear error message to the user
        alert(`API Error: ${error.message}`);
    } finally {
        // Restore the button
        btn.innerText = originalText;
        btn.disabled = false;
    }
}