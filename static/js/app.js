/* static/js/app.js */

// Global state variables
let lastResult = null;
let historyLog = [];

// DOM Element References
const themeToggle = document.getElementById('theme-toggle');
const verifyBtn = document.getElementById('verify-btn');
const resetBtn = document.getElementById('reset-btn');
const downloadPdfBtn = document.getElementById('download-pdf-btn');
const exampleDropdownBtn = document.getElementById('example-dropdown-btn');
const exampleDropdownMenu = document.getElementById('example-dropdown-menu');

const preconditionInput = document.getElementById('precondition-input');
const programInput = document.getElementById('program-input');
const postconditionInput = document.getElementById('postcondition-input');

const minValInput = document.getElementById('min-val');
const maxValInput = document.getElementById('max-val');
const numTestsInput = document.getElementById('num-tests');
const randomTestsCheckbox = document.getElementById('random-tests');

const resultsPlaceholder = document.getElementById('results-placeholder');
const resultsLoading = document.getElementById('results-loading');
const resultsDashboard = document.getElementById('results-dashboard');

const statusBanner = document.getElementById('status-banner');
const statGenerated = document.getElementById('stat-generated');
const statExecuted = document.getElementById('stat-executed');
const statIgnored = document.getElementById('stat-ignored');
const statTime = document.getElementById('stat-time');

const counterexamplesSection = document.getElementById('counterexamples-section');
const counterexamplesList = document.getElementById('counterexamples-list');
const successDetailsSection = document.getElementById('success-details-section');

const historyList = document.getElementById('history-list');
const historyCountBadge = document.getElementById('history-count');
const toastContainer = document.getElementById('toast-container');

// Core Application Initializer
document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize theme from localStorage
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    // 2. Add event listeners for editors to sync line numbers and scrolls
    setupEditorLineNumbers('precondition-input', 'precondition-lines');
    setupEditorLineNumbers('program-input', 'program-lines');
    setupEditorLineNumbers('postcondition-input', 'postcondition-lines');

    // 3. Document Collapsibles Logic
    setupCollapsible('docs-toggle-header', 'docs-body');
    setupCollapsible('history-toggle-header', 'history-body');

    // 4. Verify & Action buttons
    verifyBtn.addEventListener('click', executeVerification);
    resetBtn.addEventListener('click', resetAll);
    downloadPdfBtn.addEventListener('click', downloadPDFReport);

    // 5. Help click documentation pop
    document.getElementById('help-btn').addEventListener('click', () => {
        const docHeader = document.getElementById('docs-toggle-header');
        docHeader.parentElement.classList.add('active');
        docHeader.nextElementSibling.style.maxHeight = '1000px';
        docHeader.scrollIntoView({ behavior: 'smooth' });
        showToast('Documentation panel expanded.', 'info');
    });

    // 6. Dropdown toggle logic
    exampleDropdownBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        exampleDropdownMenu.classList.toggle('show');
    });

    document.addEventListener('click', () => {
        exampleDropdownMenu.classList.remove('show');
    });

    // Seed default examples
    loadExample(1);
});

// Editor Line Number Synchronization
function setupEditorLineNumbers(inputId, linesId) {
    const input = document.getElementById(inputId);
    const lines = document.getElementById(linesId);
    if (!input || !lines) return;

    const syncLines = () => {
        const text = input.value;
        const lineCount = text.split('\n').length;
        let html = '';
        for (let i = 1; i <= lineCount; i++) {
            html += `<div>${i}</div>`;
        }
        lines.innerHTML = html;
        lines.scrollTop = input.scrollTop; // keep scroll in sync
    };

    input.addEventListener('input', syncLines);
    input.addEventListener('scroll', () => {
        lines.scrollTop = input.scrollTop;
    });

    // Call once to initialize
    syncLines();
}

// Clear particular editor content
window.clearEditor = function(editorName) {
    const input = document.getElementById(`${editorName}-input`);
    const lines = document.getElementById(`${editorName}-lines`);
    if (input) {
        input.value = '';
        input.focus();
        // Sync lines
        let html = '<div>1</div>';
        if (lines) lines.innerHTML = html;
        showToast(`Cleared ${editorName} editor.`, 'info');
    }
};

// Collapsible Element System
function setupCollapsible(headerId, bodyId) {
    const header = document.getElementById(headerId);
    const body = document.getElementById(bodyId);
    if (!header || !body) return;

    header.addEventListener('click', () => {
        const container = header.parentElement;
        container.classList.toggle('active');
        if (container.classList.contains('active')) {
            body.style.maxHeight = body.scrollHeight + 100 + 'px';
        } else {
            body.style.maxHeight = '0px';
        }
    });
}

// Load Example Presets
window.loadExample = function(index) {
    const examples = {
        1: {
            pre: "x >= 0",
            prog: "x := x + 1;",
            post: "x > 0",
            title: "Increment ({x >= 0} x := x + 1 {x > 0})"
        },
        2: {
            pre: "x > 5",
            prog: "x := x - 10;",
            post: "x > 0",
            title: "Bad Offset ({x > 5} x := x - 10 {x > 0})"
        },
        3: {
            pre: "true",
            prog: "if x < 0 then\n    y := 0 - x\nelse\n    y := x\nend",
            post: "y >= 0",
            title: "Absolute Value"
        },
        4: {
            pre: "x == 0 and y == 5",
            prog: "while y > 0 do\n    x := x + 2;\n    y := y - 1\nend",
            post: "x == 10",
            title: "Loop Multiplier"
        },
        5: {
            pre: "true",
            prog: "x := 10 / y;",
            post: "x > 0",
            title: "Div Zero"
        },
        6: {
            pre: "true",
            prog: "while x == 0 do\n    skip\nend",
            post: "x != 0",
            title: "Infinite Loop"
        }
    };

    const ex = examples[index];
    if (!ex) return;

    preconditionInput.value = ex.pre;
    programInput.value = ex.prog;
    postconditionInput.value = ex.post;

    // Trigger input events to refresh line numbers
    preconditionInput.dispatchEvent(new Event('input'));
    programInput.dispatchEvent(new Event('input'));
    postconditionInput.dispatchEvent(new Event('input'));

    showToast(`Loaded example: ${ex.title}`, 'success');
};

// Dark Mode Switcher logic
themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    showToast(`Switched to ${newTheme} mode.`, 'info');
});

// Toast Notification Manager
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Choose matching icon
    let iconClass = 'fa-circle-info';
    if (type === 'success') iconClass = 'fa-circle-check';
    if (type === 'error') iconClass = 'fa-circle-exclamation';
    if (type === 'warning') iconClass = 'fa-triangle-exclamation';
    
    toast.innerHTML = `
        <i class="fa-solid ${iconClass} toast-icon"></i>
        <div class="toast-content">
            <div class="toast-title">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
            <div class="toast-msg">${message}</div>
        </div>
        <button class="toast-close">&times;</button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Slide in
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Auto dismiss after 4 seconds
    const dismissTimer = setTimeout(() => dismissToast(toast), 4000);
    
    // Manual dismiss
    toast.querySelector('.toast-close').addEventListener('click', () => {
        clearTimeout(dismissTimer);
        dismissToast(toast);
    });
}

function dismissToast(toast) {
    toast.classList.remove('show');
    // Remove element after transition completes
    toast.addEventListener('transitionend', () => toast.remove());
}

// Reset Control and Editor panels
function resetAll() {
    preconditionInput.value = '';
    programInput.value = '';
    postconditionInput.value = '';

    preconditionInput.dispatchEvent(new Event('input'));
    programInput.dispatchEvent(new Event('input'));
    postconditionInput.dispatchEvent(new Event('input'));

    minValInput.value = '-10';
    maxValInput.value = '10';
    numTestsInput.value = '100';
    randomTestsCheckbox.checked = true;

    // Reset dashboard view
    resultsDashboard.classList.add('hidden');
    resultsLoading.classList.add('hidden');
    resultsPlaceholder.classList.remove('hidden');

    lastResult = null;

    showToast('Settings and editor inputs reset to defaults.', 'info');
}

// Trigger Verification Request
async function executeVerification() {
    const precondition = preconditionInput.value.trim();
    const program = programInput.value.trim();
    const postcondition = postconditionInput.value.trim();

    // Client-side validations
    if (!precondition) {
        showToast('Precondition field is required.', 'error');
        preconditionInput.focus();
        return;
    }
    if (!program) {
        showToast('Program instructions are required.', 'error');
        programInput.focus();
        return;
    }
    if (!postcondition) {
        showToast('Postcondition field is required.', 'error');
        postconditionInput.focus();
        return;
    }

    const minVal = parseInt(minValInput.value);
    const maxVal = parseInt(maxValInput.value);
    const numTests = parseInt(numTestsInput.value);
    const randomize = randomTestsCheckbox.checked;

    if (isNaN(minVal) || isNaN(maxVal)) {
        showToast('Min/Max range values must be integers.', 'error');
        return;
    }
    if (minVal > maxVal) {
        showToast('Minimum range cannot exceed Maximum range.', 'error');
        return;
    }
    if (isNaN(numTests) || numTests <= 0) {
        showToast('Number of tests must be a positive integer.', 'error');
        return;
    }

    // Prepare visual state to Loading
    resultsPlaceholder.classList.add('hidden');
    resultsDashboard.classList.add('hidden');
    resultsLoading.classList.remove('hidden');
    verifyBtn.disabled = true;

    try {
        const response = await fetch('/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                precondition,
                program,
                postcondition,
                num_tests: numTests,
                min_val: minVal,
                max_val: maxVal,
                randomize: randomize
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.message || 'Verification request failed.');
        }

        const data = await response.json();
        
        if (!data.success) {
            // Check for parsing errors
            showToast(`${data.error_type}: ${data.message}`, 'error');
            displayParseError(data.error_type, data.message);
        } else {
            // Process valid response data
            lastResult = data;
            renderResults(data);
            logHistory(precondition, program, postcondition, data);
            showToast(data.valid ? 'Hoare Triplet is VALID!' : 'Hoare Triplet is INVALID.', data.valid ? 'success' : 'error');
        }

    } catch (err) {
        showToast(err.message, 'error');
        displayParseError('Network / Server Error', err.message);
    } finally {
        resultsLoading.classList.add('hidden');
        verifyBtn.disabled = false;
    }
}

// Display Parser/Server error banner
function displayParseError(errorType, message) {
    resultsDashboard.classList.remove('hidden');
    
    // Status banner
    statusBanner.className = 'status-banner status-banner-invalid';
    statusBanner.innerHTML = `
        <i class="fa-solid fa-triangle-exclamation status-icon"></i>
        <div>
            <div>${errorType}</div>
            <div style="font-size: 13px; font-weight: 400; opacity: 0.9; margin-top: 4px;">${message}</div>
        </div>
    `;

    // Reset statistics to 0
    statGenerated.innerText = '0';
    statExecuted.innerText = '0';
    statIgnored.innerText = '0';
    statTime.innerText = '0 ms';

    // Hide success and show nothing in counterexamples
    successDetailsSection.classList.add('hidden');
    counterexamplesSection.classList.add('hidden');
    counterexamplesList.innerHTML = '';
}

// Render execution stats and results
function renderResults(data) {
    resultsDashboard.classList.remove('hidden');

    // 1. Render Banner
    if (data.valid) {
        statusBanner.className = 'status-banner status-banner-valid';
        statusBanner.innerHTML = `
            <i class="fa-solid fa-circle-check status-icon"></i>
            <div>
                <div>✓ Hoare Triplet is Valid</div>
                <div style="font-size: 13px; font-weight: 400; opacity: 0.9; margin-top: 4px;">Verified over ${data.passed_tests} executing states.</div>
            </div>
        `;
        successDetailsSection.classList.remove('hidden');
        counterexamplesSection.classList.add('hidden');
    } else {
        statusBanner.className = 'status-banner status-banner-invalid';
        statusBanner.innerHTML = `
            <i class="fa-solid fa-circle-xmark status-icon"></i>
            <div>
                <div>✗ Hoare Triplet is Invalid</div>
                <div style="font-size: 13px; font-weight: 400; opacity: 0.9; margin-top: 4px;">Found ${data.failed_tests} violating counterexamples.</div>
            </div>
        `;
        successDetailsSection.classList.add('hidden');
        counterexamplesSection.classList.remove('hidden');
        
        // Populate counterexample cards
        renderCounterexamples(data.counterexamples);
    }

    // 2. Populate stats with counter animation
    animateValue('stat-generated', 0, data.total_tests, 400);
    animateValue('stat-executed', 0, data.passed_tests + data.failed_tests, 400);
    animateValue('stat-ignored', 0, data.ignored_tests, 400);
    statTime.innerText = data.execution_time_str;
}

// Animate numbers for dashboards
function animateValue(id, start, end, duration) {
    if (start === end) {
        document.getElementById(id).innerHTML = end;
        return;
    }
    const obj = document.getElementById(id);
    const range = end - start;
    let current = start;
    const increment = end > start ? 1 : -1;
    const stepTime = Math.abs(Math.floor(duration / range));
    const timer = setInterval(() => {
        current += increment;
        obj.innerHTML = current;
        if (current === end) {
            clearInterval(timer);
        }
    }, Math.max(stepTime, 10));
}

// Render individual counterexample cards
function renderCounterexamples(list) {
    counterexamplesList.innerHTML = '';
    
    if (!list || list.length === 0) {
        counterexamplesList.innerHTML = '<div class="text-muted text-center py-4">No counterexamples found.</div>';
        return;
    }

    list.forEach((ce, index) => {
        const card = document.createElement('div');
        card.className = 'ce-card';
        card.style.animationDelay = `${index * 50}ms`;

        // Check if there is an execution error vs simple postcondition violation
        let isError = ce.error !== null;
        let headerText = isError ? 'Execution Crash' : 'Assertion Violation';
        let detailText = isError ? ce.error : ce.violation;

        card.innerHTML = `
            <div class="ce-header">
                <span class="ce-title" style="color: ${isError ? 'var(--warning)' : 'var(--error)'}">
                    <i class="fa-solid ${isError ? 'fa-triangle-exclamation' : 'fa-circle-xmark'}"></i> ${headerText}
                </span>
                <span class="ce-badge" style="background-color: ${isError ? 'rgba(245, 158, 11, 0.1)' : 'rgba(239, 68, 68, 0.1)'}; color: ${isError ? 'var(--warning)' : 'var(--error)'}">
                    CE #${index + 1}
                </span>
            </div>
            
            <div class="ce-flow">
                <div class="ce-state-box">
                    <span class="ce-state-label">Initial State</span>
                    <span class="ce-state-vals">${escapeHtml(ce.initial_state)}</span>
                </div>
                <div class="ce-arrow"><i class="fa-solid fa-chevron-right"></i></div>
                <div class="ce-state-box">
                    <span class="ce-state-label">Final State</span>
                    <span class="ce-state-vals">${ce.final_state ? escapeHtml(ce.final_state) : '<span class="text-error">Aborted</span>'}</span>
                </div>
            </div>
            
            <div class="ce-fail-box" style="border-color: ${isError ? 'rgba(245, 158, 11, 0.3)' : 'rgba(239, 68, 68, 0.3)'}">
                <div class="ce-fail-title" style="color: ${isError ? 'var(--warning)' : 'var(--error)'}">
                    ${isError ? 'Runtime Exception Trace' : 'Failed Predicate'}
                </div>
                <div class="ce-fail-cond">${escapeHtml(detailText)}</div>
            </div>
        `;
        counterexamplesList.appendChild(card);
    });
}

// Log history of verification runs
function logHistory(pre, prog, post, result) {
    const timestamp = new Date().toLocaleTimeString();
    
    // Limit program snippet for table
    let progSnippet = prog;
    if (progSnippet.length > 25) {
        progSnippet = progSnippet.substring(0, 22) + '...';
    }

    const item = {
        timestamp,
        pre,
        prog,
        post,
        valid: result.valid,
        total: result.total_tests,
        passed: result.passed_tests,
        failed: result.failed_tests,
        ignored: result.ignored_tests,
        time_str: result.execution_time_str
    };

    historyLog.unshift(item); // insert at top
    // Limit to max 10 records
    if (historyLog.length > 10) {
        historyLog.pop();
    }

    // Refresh History table UI
    historyCountBadge.innerText = historyLog.length;
    renderHistoryTable();
}

function renderHistoryTable() {
    historyList.innerHTML = '';
    
    if (historyLog.length === 0) {
        historyList.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">No runs logged in this session yet.</td>
            </tr>
        `;
        return;
    }

    historyLog.forEach((item, index) => {
        const tr = document.createElement('tr');
        
        let statusBadge = '';
        if (item.valid) {
            statusBadge = '<span class="history-status-badge hs-valid"><i class="fa-solid fa-check"></i> Valid</span>';
        } else {
            statusBadge = `<span class="history-status-badge hs-invalid"><i class="fa-solid fa-xmark"></i> Invalid (${item.failed})</span>`;
        }

        tr.innerHTML = `
            <td>${item.timestamp}</td>
            <td><code>${escapeHtml(item.pre)}</code></td>
            <td><code>${escapeHtml(item.prog)}</code></td>
            <td><code>${escapeHtml(item.post)}</code></td>
            <td>${statusBadge}</td>
            <td>
                <button class="btn btn-outline btn-sm" onclick="loadHistoryItem(${index})" style="padding: 4px 8px; font-size: 12px; border-radius: 6px;">
                    Load
                </button>
            </td>
        `;
        historyList.appendChild(tr);
    });
}

// Load inputs from history item
window.loadHistoryItem = function(index) {
    const item = historyLog[index];
    if (!item) return;

    preconditionInput.value = item.pre;
    programInput.value = item.prog;
    postconditionInput.value = item.post;

    preconditionInput.dispatchEvent(new Event('input'));
    programInput.dispatchEvent(new Event('input'));
    postconditionInput.dispatchEvent(new Event('input'));

    showToast('Loaded inputs from verification log history.', 'success');
};

// Generate high quality print layout and download PDF report
function downloadPDFReport() {
    if (!lastResult) {
        showToast('No verification results available. Run verify first.', 'warning');
        return;
    }

    const pre = preconditionInput.value.trim();
    const prog = programInput.value.trim();
    const post = postconditionInput.value.trim();
    const minVal = minValInput.value;
    const maxVal = maxValInput.value;
    const numTests = numTestsInput.value;
    const isVal = lastResult.valid;

    // Create report body
    const el = document.getElementById('printable-report');
    el.innerHTML = `
        <div style="padding: 24px; font-family: 'Inter', sans-serif; color: #2D3748;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #007BFF; padding-bottom: 12px; margin-bottom: 24px;">
                <div>
                    <h1 style="font-size: 26px; margin: 0; color: #007BFF;">Hoare Triplet Verification Report</h1>
                    <span style="font-size: 13px; color: #718096; font-weight: 500;">Formal Verification through Testing State Cases</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 13px; color: #718096; font-weight: 500; display: block;">Generated On:</span>
                    <span style="font-size: 14px; font-weight: 600; color: #2D3748;">${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}</span>
                </div>
            </div>

            <div style="margin-bottom: 24px;">
                <h2 style="font-size: 16px; border-bottom: 1px solid #DCE7EC; padding-bottom: 6px; margin-bottom: 12px; color: #2D3748;">1. Triplet Details</h2>
                <table style="width: 100%; border-collapse: collapse; border: 1px solid #DCE7EC; font-size: 13px; margin-bottom: 16px;">
                    <tr>
                        <td style="padding: 8px 12px; background-color: #F8FBFC; border: 1px solid #DCE7EC; font-weight: 600; width: 140px;">Precondition {P}</td>
                        <td style="padding: 8px 12px; border: 1px solid #DCE7EC; font-family: monospace; color: #007BFF;">${escapeHtml(pre)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 12px; background-color: #F8FBFC; border: 1px solid #DCE7EC; font-weight: 600;">Program {C}</td>
                        <td style="padding: 8px 12px; border: 1px solid #DCE7EC; font-family: monospace; white-space: pre-wrap;">${escapeHtml(prog)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 12px; background-color: #F8FBFC; border: 1px solid #DCE7EC; font-weight: 600;">Postcondition {Q}</td>
                        <td style="padding: 8px 12px; border: 1px solid #DCE7EC; font-family: monospace; color: #22C55E;">${escapeHtml(post)}</td>
                    </tr>
                </table>
            </div>

            <div style="margin-bottom: 24px;">
                <h2 style="font-size: 16px; border-bottom: 1px solid #DCE7EC; padding-bottom: 6px; margin-bottom: 12px; color: #2D3748;">2. Generator & Range Config</h2>
                <table style="width: 100%; border-collapse: collapse; border: 1px solid #DCE7EC; font-size: 13px;">
                    <tr>
                        <td style="padding: 8px 12px; background-color: #F8FBFC; border: 1px solid #DCE7EC; font-weight: 600; width: 180px;">Integer Range Boundary</td>
                        <td style="padding: 8px 12px; border: 1px solid #DCE7EC;">[ ${minVal} , ${maxVal} ]</td>
                        <td style="padding: 8px 12px; background-color: #F8FBFC; border: 1px solid #DCE7EC; font-weight: 600; width: 180px;">Requested Test Count</td>
                        <td style="padding: 8px 12px; border: 1px solid #DCE7EC;">${numTests}</td>
                    </tr>
                </table>
            </div>

            <div style="margin-bottom: 24px;">
                <h2 style="font-size: 16px; border-bottom: 1px solid #DCE7EC; padding-bottom: 6px; margin-bottom: 12px; color: #2D3748;">3. Verification Summary</h2>
                <div style="display: flex; gap: 12px; margin-bottom: 16px;">
                    <div style="flex: 1.5; padding: 12px; border-radius: 8px; background-color: ${isVal ? '#EAFAF1' : '#FCECEE'}; border: 1px solid ${isVal ? '#A3E635' : '#FECACA'}; text-align: center;">
                        <span style="font-size: 11px; text-transform: uppercase; color: #718096; display: block; font-weight: 600;">Overall Status</span>
                        <span style="font-size: 20px; font-weight: 700; color: ${isVal ? '#15803D' : '#B91C1C'};">${isVal ? 'VALID TRIPLET' : 'INVALID TRIPLET'}</span>
                    </div>
                    <div style="flex: 1; padding: 12px; border-radius: 8px; background-color: #F8FBFC; border: 1px solid #DCE7EC; text-align: center;">
                        <span style="font-size: 11px; text-transform: uppercase; color: #718096; display: block; font-weight: 600;">Tests Executed</span>
                        <span style="font-size: 20px; font-weight: 700;">${lastResult.passed_tests + lastResult.failed_tests}</span>
                    </div>
                    <div style="flex: 1; padding: 12px; border-radius: 8px; background-color: #F8FBFC; border: 1px solid #DCE7EC; text-align: center;">
                        <span style="font-size: 11px; text-transform: uppercase; color: #718096; display: block; font-weight: 600;">Execution Time</span>
                        <span style="font-size: 20px; font-weight: 700;">${lastResult.execution_time_str}</span>
                    </div>
                </div>

                <table style="width: 100%; border-collapse: collapse; border: 1px solid #DCE7EC; font-size: 13px;">
                    <thead>
                        <tr style="background-color: #F8FBFC;">
                            <th style="padding: 8px 12px; border: 1px solid #DCE7EC; text-align: left;">Metric</th>
                            <th style="padding: 8px 12px; border: 1px solid #DCE7EC; text-align: right;">Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="padding: 8px 12px; border: 1px solid #DCE7EC;">Total Unique States Generated</td>
                            <td style="padding: 8px 12px; border: 1px solid #DCE7EC; text-align: right;">${lastResult.total_tests}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 12px; border: 1px solid #DCE7EC;">Passed Test Cases (Satisfied Postcondition)</td>
                            <td style="padding: 8px 12px; border: 1px solid #DCE7EC; text-align: right; color: #16A34A; font-weight: 600;">${lastResult.passed_tests}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 12px; border: 1px solid #DCE7EC;">Failed Test Cases (Violated Postcondition/Crash)</td>
                            <td style="padding: 8px 12px; border: 1px solid #DCE7EC; text-align: right; color: #DC2626; font-weight: 600;">${lastResult.failed_tests}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 12px; border: 1px solid #DCE7EC;">Ignored States (Precondition Evaluated to False)</td>
                            <td style="padding: 8px 12px; border: 1px solid #DCE7EC; text-align: right; color: #718096;">${lastResult.ignored_tests}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            ${!isVal && lastResult.counterexamples.length > 0 ? `
            <div style="page-break-before: auto; margin-top: 24px;">
                <h2 style="font-size: 16px; border-bottom: 1px solid #DCE7EC; padding-bottom: 6px; margin-bottom: 12px; color: #2D3748;">4. Violations / Counterexamples</h2>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    ${lastResult.counterexamples.map((ce, i) => `
                        <div style="border: 1px solid #FECACA; border-left: 4px solid #EF4444; border-radius: 6px; padding: 12px; font-size: 12px; background-color: #FDF2F2;">
                            <div style="font-weight: 700; color: #B91C1C; margin-bottom: 6px;">Counterexample #${i + 1} - ${escapeHtml(ce.violation)}</div>
                            <div style="margin-bottom: 4px;"><strong>Initial State:</strong> <code style="background-color:rgba(0,0,0,0.05); padding:1px 4px; border-radius:3px;">${escapeHtml(ce.initial_state)}</code></div>
                            <div style="margin-bottom: 4px;"><strong>Final State:</strong> <code style="background-color:rgba(0,0,0,0.05); padding:1px 4px; border-radius:3px;">${ce.final_state ? escapeHtml(ce.final_state) : 'ABORTED'}</code></div>
                            ${ce.error ? `<div style="color: #9B2C2C; margin-top: 4px; padding: 4px; border: 1px dashed rgba(239,68,68,0.2); font-family: monospace; background:#FFF5F5;"><strong>Error:</strong> ${escapeHtml(ce.error)}</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
        </div>
    `;

    // pdf configuration parameters
    const opt = {
        margin:       10,
        filename:     `hoare-verification-report-${Date.now()}.pdf`,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    html2pdf().set(opt).from(el).save();
    showToast('Compiling PDF document and starting download.', 'success');
}

// Escape HTML characters to prevent XSS
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}
