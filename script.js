const uploadedFiles = { tender: null, bids: [] };
let evaluationResults = null;

document.addEventListener('DOMContentLoaded', () => {
    const tenderInput = document.getElementById('tenderFile');
    const bidsInput = document.getElementById('bidFiles');

    tenderInput.addEventListener('change', e => handleTenderUpload(e.target.files[0]));
    bidsInput.addEventListener('change', e => handleBidUpload(e.target.files));
    setupDragAndDrop();
});

function setupDragAndDrop() {
    ['tenderUpload', 'bidsUpload'].forEach(id => {
        const box = document.getElementById(id);
        box.addEventListener('dragover', e => {
            e.preventDefault();
            box.style.borderColor = '#667eea';
            box.style.background = '#f7fafc';
        });
        box.addEventListener('dragleave', e => {
            e.preventDefault();
            box.style.borderColor = '#cbd5e0';
            box.style.background = 'white';
        });
        box.addEventListener('drop', e => {
            e.preventDefault();
            box.style.borderColor = '#cbd5e0';
            box.style.background = 'white';
            const files = e.dataTransfer.files;
            id === 'tenderUpload' ? handleTenderUpload(files[0]) : handleBidUpload(files);
        });
    });
}

function handleTenderUpload(file) {
    if (!file || file.type !== 'application/pdf') return alert('Please upload a PDF file');
    uploadedFiles.tender = file;
    updateFileList();
}

function handleBidUpload(files) {
    if (!files) return;
    for (const file of files) {
        if (file.type !== 'application/pdf') {
            alert(`${file.name} is not a PDF. Please upload only PDF files.`);
            continue;
        }
        if (!uploadedFiles.bids.some(f => f.name === file.name)) uploadedFiles.bids.push(file);
    }
    updateFileList();
}

function updateFileList() {
    const fileList = document.getElementById('fileList');
    fileList.innerHTML = '';

    // Show tender if uploaded
    if (uploadedFiles.tender) {
        const item = createFileListItem(uploadedFiles.tender, 'tender');
        fileList.appendChild(item);
    }

    // Show bids
    uploadedFiles.bids.forEach((file, index) => {
        const item = createFileListItem(file, 'bid', index);
        fileList.appendChild(item);
    });

    if (!uploadedFiles.tender && uploadedFiles.bids.length === 0) {
        fileList.innerHTML = '<p style="color: #718096; text-align: center;">No files uploaded yet</p>';
    }
}

function createFileListItem(file, type, index) {
    const div = document.createElement('div');
    div.className = 'file-item';

    const fileSize = (file.size / 1024).toFixed(2);

    div.innerHTML = `
        <span class="file-name">
            ${type === 'tender' ? '📄 Tender: ' : '📑 Bid: '}${file.name}
        </span>
        <span class="file-size">${fileSize} KB</span>
        <span class="remove-file" onclick="removeFile('${type}', ${index})">×</span>
    `;

    return div;
}

function removeFile(type, index) {
    if (type === 'tender') {
        uploadedFiles.tender = null;
    } else {
        uploadedFiles.bids.splice(index, 1);
    }
    updateFileList();
}

async function evaluateBids() {
    // Validate inputs
    if (!uploadedFiles.tender) {
        alert('Please upload the tender document first');
        return;
    }

    if (uploadedFiles.bids.length === 0) {
        alert('Please upload at least one bid proposal');
        return;
    }

    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('evaluateBtn').disabled = true;
    document.getElementById('resultsSection').style.display = 'none';

    try {
        // In a real system, you would send files to backend
        // For demo, we'll simulate AI processing

        await simulateProcessing();

        // Generate results
        evaluationResults = generateMockResults();

        // Display results
        displayResults(evaluationResults);

    } catch (error) {
        console.error('Evaluation error:', error);
        alert('Error during evaluation. Please try again.');
    } finally {
        // Hide loading
        document.getElementById('loading').style.display = 'none';
        document.getElementById('evaluateBtn').disabled = false;
    }
}

async function simulateProcessing() {
    return new Promise(resolve => {
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10;
            document.querySelector('#loading p').textContent =
                `AI is analyzing bids... ${progress}% complete`;

            if (progress >= 100) {
                clearInterval(interval);
                resolve();
            }
        }, 300);
    });
}

function generateMockResults() {
    const companies = [
        { name: 'Odisha Infrastructure Ltd', experience: 8, turnover: 15.2 },
        { name: 'Bhubaneswar Constructions', experience: 5, turnover: 8.7 },
        { name: 'Eastern Builders Pvt Ltd', experience: 12, turnover: 25.0 },
        { name: 'Utkal Engineering Works', experience: 3, turnover: 5.5 },
        { name: 'Mahanadi Projects', experience: 7, turnover: 12.3 }
    ];

    const bids = uploadedFiles.bids.map((_, i) => {
        const company = companies[i % companies.length];
        const bidAmount = 1e7 + Math.random() * 5e6;
        const missingDocs = [];
        if (Math.random() > 0.7) missingDocs.push('GST Certificate');
        if (Math.random() > 0.8) missingDocs.push('EPF Registration');
        const complianceScore = 100 - missingDocs.length * 20;
        const experienceScore = Math.min(100, (company.experience / 10) * 100);
        const priceScore = Math.random() * 30 + 70;
        const technicalScore = complianceScore * 0.4 + experienceScore * 0.6;
        const totalScore = technicalScore * 0.7 + priceScore * 0.3;
        let status =
            missingDocs.length ? 'Non-Compliant' :
            totalScore >= 80 ? 'Highly Recommended' :
            totalScore >= 60 ? 'Recommended' :
            'Not Recommended';
        return {
            rank: 0,
            company: company.name,
            totalScore: Math.round(totalScore),
            status,
            compliance: `${complianceScore}% (Missing: ${missingDocs.join(', ') || 'None'})`,
            bidAmount,
            experience: `${company.experience} years`,
            details: { documents: missingDocs, yearsExperience: company.experience, turnover: company.turnover }
        };
    });

    bids.sort((a, b) => b.totalScore - a.totalScore);
    bids.forEach((b, idx) => (b.rank = idx + 1));

    const riskFlags = [];
    if (Math.random() > 0.5) riskFlags.push({ type: 'Suspicious Pricing Pattern', description: 'Two bidders have identical pricing structures', severity: 'High' });
    if (Math.random() > 0.6) riskFlags.push({ type: 'Missing Documents', description: '3 bidders missing mandatory GST certificates', severity: 'High' });
    if (Math.random() > 0.7) riskFlags.push({ type: 'Insufficient Experience', description: '2 bidders have less than required 5 years experience', severity: 'Medium' });

    return {
        bids,
        summary: {
            total: bids.length,
            highlyRecommended: bids.filter(b => b.status === 'Highly Recommended').length,
            recommended: bids.filter(b => b.status === 'Recommended').length,
            notRecommended: bids.filter(b => b.status === 'Not Recommended').length,
            nonCompliant: bids.filter(b => b.status === 'Non-Compliant').length
        },
        riskFlags
    };
}

function displayResults(results) {
    // Update summary cards
    const summaryHtml = `
        <div class="summary-card card-highly">
            <h4>Highly Recommended</h4>
            <div class="number">${results.summary.highlyRecommended}</div>
        </div>
        <div class="summary-card card-recommended">
            <h4>Recommended</h4>
            <div class="number">${results.summary.recommended}</div>
        </div>
        <div class="summary-card card-not">
            <h4>Not Recommended</h4>
            <div class="number">${results.summary.notRecommended}</div>
        </div>
        <div class="summary-card card-non">
            <h4>Non-Compliant</h4>
            <div class="number">${results.summary.nonCompliant}</div>
        </div>
    `;
    document.getElementById('summaryCards').innerHTML = summaryHtml;

    // Update results table
    const tableBody = document.getElementById('resultsBody');
    tableBody.innerHTML = '';

    results.bids.forEach(bid => {
        const row = document.createElement('tr');

        // Determine status class
        let statusClass = '';
        if (bid.status === 'Highly Recommended') statusClass = 'status-highly';
        else if (bid.status === 'Recommended') statusClass = 'status-recommended';
        else if (bid.status === 'Not Recommended') statusClass = 'status-not';
        else statusClass = 'status-non';

        row.innerHTML = `
            <td><strong>#${bid.rank}</strong></td>
            <td>${bid.company}</td>
            <td><strong>${bid.totalScore}%</strong></td>
            <td><span class="status-badge ${statusClass}">${bid.status}</span></td>
            <td>${bid.compliance}</td>
            <td>₹${(bid.bidAmount / 10000000).toFixed(2)} Cr</td>
            <td>${bid.experience}</td>
            <td>
                <span class="tooltip">ℹ️
                    <span class="tooltiptext">
                        Turnover: ₹${bid.details.turnover}Cr<br>
                        Documents: ${bid.details.documents.length || 'All present'}
                    </span>
                </span>
            </td>
        `;

        tableBody.appendChild(row);
    });

    // Update risk flags
    const riskDiv = document.getElementById('riskFlags');
    if (results.riskFlags.length > 0) {
        let riskHtml = '';
        results.riskFlags.forEach(flag => {
            const severityClass = `severity-${flag.severity.toLowerCase()}`;
            riskHtml += `
                <div class="risk-item">
                    <h4>
                        ${flag.type}
                        <span class="severity ${severityClass}">${flag.severity}</span>
                    </h4>
                    <p>${flag.description}</p>
                </div>
            `;
        });
        riskDiv.innerHTML = riskHtml;
    } else {
        riskDiv.innerHTML = '<p style="color: #48bb78;">✓ No significant risks detected</p>';
    }

    // Show results section
    document.getElementById('resultsSection').style.display = 'block';

    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

function exportReport() {
    if (!evaluationResults) {
        alert('No results to export');
        return;
    }

    // Create report object
    const report = {
        generatedAt: new Date().toISOString(),
        tenderFile: uploadedFiles.tender ? uploadedFiles.tender.name : null,
        totalBids: uploadedFiles.bids.length,
        evaluationResults: evaluationResults
    };

    // Convert to JSON
    const reportJson = JSON.stringify(report, null, 2);

    // Download
    const blob = new Blob([reportJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tender-evaluation-report-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    alert('Report downloaded successfully!');
}

// Reset system
function resetSystem() {
    if (!confirm('Are you sure? All uploaded files and results will be cleared.')) return;
    uploadedFiles.tender = null;
    uploadedFiles.bids = [];
    evaluationResults = null;
    updateFileList();
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('tenderFile').value = '';
    document.getElementById('bidFiles').value = '';
}