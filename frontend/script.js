/*
============================================
STARTUP IDEA VALIDATOR - FRONTEND LOGIC
============================================
Handles form submission, API calls, and result display
*/

// ============================================
// CONFIGURATION
// ============================================
const API_BASE_URL = 'http://localhost:8000';  // FastAPI backend URL
const DISTRIBUTION_APP_URL = 'http://localhost:5001'; // <-- Flask app URL/port

let lastIdeaInput = null; // store the last form submission

// ============================================
// DOM ELEMENTS
// ============================================

// Sections
const inputSection = document.getElementById('input-section');
const loadingSection = document.getElementById('loading-section');
const resultsSection = document.getElementById('results-section');

// Form
const ideaForm = document.getElementById('idea-form');
const submitBtn = document.getElementById('submit-btn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoader = submitBtn.querySelector('.btn-loader');

// Loading
const loadingStatus = document.getElementById('loading-status');
const step1 = document.getElementById('step1');
const step2 = document.getElementById('step2');
const step3 = document.getElementById('step3');
const step4 = document.getElementById('step4');

// Results
const resultsContent = document.getElementById('results-content');
const newValidationBtn = document.getElementById('new-validation-btn');
const nextStepBtn = document.getElementById('next-step-btn');

// ============================================
// EVENT LISTENERS
// ============================================

// Form submission
ideaForm.addEventListener('submit', handleFormSubmit);

// New validation button
newValidationBtn.addEventListener('click', resetToForm);
nextStepBtn.addEventListener('click', goToDistribution);

// ============================================
// MAIN FUNCTIONS
// ============================================

/**
 * Handle form submission
 * 1. Validate form
 * 2. Collect data
 * 3. Show loading screen
 * 4. Call API
 * 5. Show results
 */
async function handleFormSubmit(e) {
    e.preventDefault();
    
    console.log('📝 Form submitted');
    
    // Collect form data
    const formData = new FormData(ideaForm);
    const ideaInput = {
        idea_name: formData.get('idea_name'),
        problem: formData.get('problem'),
        why_problem_exists: formData.get('why_problem_exists'),
        target_audience: formData.get('target_audience'),
        solution: formData.get('solution'),
        key_features: formData.get('key_features'),
        uniqueness: formData.get('uniqueness'),
        market: formData.get('market'),
        revenue_model: formData.get('revenue_model'),
        expected_users: formData.get('expected_users'),
        region: formData.get('region'),
        extra_notes: formData.get('extra_notes') || ''
    };
    lastIdeaInput = ideaInput;
    
    console.log('📦 Form data collected:', ideaInput);
    
    // Show loading screen
    showSection(loadingSection);
    startLoadingAnimation();
    
    // Call validation API
    try {
        console.log('🌐 Calling validation API...');
        const result = await validateIdea(ideaInput);
        
        if (result.success) {
            console.log('✅ Validation successful');
            displayResults(result.data);
            showSection(resultsSection);
        } else {
            console.error('❌ Validation failed:', result);
            alert('Validation failed. Please try again.');
            showSection(inputSection);
        }
    } catch (error) {
        console.error('❌ Error:', error);
        alert(`Error: ${error.message}`);
        showSection(inputSection);
    } finally {
        resetLoadingAnimation();
    }
}

/**
 * Call validation API
 * Makes POST request to FastAPI backend
 */
async function validateIdea(ideaInput) {
    const response = await fetch(`${API_BASE_URL}/api/validate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(ideaInput)
    });
    
    if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
    }
    
    return await response.json();
}

/**
 * Display validation results
 * Builds HTML for the complete report
 */
function displayResults(data) {
    console.log('📊 Displaying results');
    
    const summary = data.final_summary;
    const competitors = data.web_research.competitors || [];
    
    const html = `
        <!-- Score Cards -->
        <div class="score-cards">
            <div class="score-card">
                <h3>Feasibility Score</h3>
                <div class="score-value">${summary.feasibility_score}</div>
                <div class="score-label">out of 100</div>
            </div>
            <div class="score-card">
                <h3>Market Readiness</h3>
                <div class="score-value">${summary.market_readiness_score}</div>
                <div class="score-label">out of 100</div>
            </div>
        </div>
        
        <!-- Overview -->
        <div class="content-block">
            <h3>📋 Executive Summary</h3>
            <p>${summary.overview}</p>
        </div>
        
        <!-- SWOT Analysis -->
        <div class="content-block">
            <h3>🎯 SWOT Analysis</h3>
            <div class="swot-grid">
                <div class="swot-box strengths">
                    <h4>💪 Strengths</h4>
                    <ul>
                        ${summary.swot_analysis.strengths.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
                <div class="swot-box weaknesses">
                    <h4>⚠️ Weaknesses</h4>
                    <ul>
                        ${summary.swot_analysis.weaknesses.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
                <div class="swot-box opportunities">
                    <h4>🚀 Opportunities</h4>
                    <ul>
                        ${summary.swot_analysis.opportunities.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
                <div class="swot-box threats">
                    <h4>⚡ Threats</h4>
                    <ul>
                        ${summary.swot_analysis.threats.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            </div>
        </div>
        
        <!-- Competitive Advantage -->
        <div class="content-block">
            <h3>🌟 Competitive Advantage</h3>
            <p>${summary.competitive_advantage}</p>
        </div>
        
        <!-- Market Size -->
        <div class="content-block">
            <h3>💰 Market Size Estimate</h3>
            <p>${summary.market_size_estimate}</p>
        </div>
        
        <!-- Competitors -->
        ${competitors.length > 0 ? `
        <div class="content-block">
            <h3>🏢 Competitors Found (${competitors.length})</h3>
            ${competitors.map(comp => `
                <div class="competitor-card">
                    <h4>${comp.name}</h4>
                    <p>${comp.description}</p>
                    <div class="competitor-meta">
                        ${comp.url ? `<span>🌐 <a href="${comp.url}" target="_blank">Website</a></span>` : ''}
                        ${comp.founders !== 'Unknown' ? `<span>👤 Founders: ${comp.founders}</span>` : ''}
                        ${comp.revenue !== 'Unknown' ? `<span>💵 Revenue: ${comp.revenue}</span>` : ''}
                        ${comp.region !== 'Unknown' ? `<span>📍 Region: ${comp.region}</span>` : ''}
                    </div>
                    ${comp.features && comp.features.length > 0 ? `
                        <div style="margin-top: 0.5rem;">
                            <strong>Key Features:</strong> ${comp.features.join(', ')}
                        </div>
                    ` : ''}
                </div>
            `).join('')}
        </div>
        ` : ''}
        
        <!-- Risk Analysis -->
        <div class="content-block">
            <h3>⚠️ Risk Analysis</h3>
            <ul>
                ${summary.risk_analysis.map(risk => `<li>${risk}</li>`).join('')}
            </ul>
        </div>
        
        <!-- Recommendations -->
        <div class="content-block">
            <h3>💡 Recommendations</h3>
            <ul>
                ${summary.recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        </div>
    `;
    
    resultsContent.innerHTML = html;
}

// ============================================
// LOADING ANIMATION
// ============================================

/**
 * Animate loading steps
 * Shows progress through validation stages
 */
function startLoadingAnimation() {
    let currentStep = 1;
    const steps = [step1, step2, step3, step4];
    const messages = [
        'Processing your input with AI...',
        'Searching the web for competitors...',
        'Analyzing market data...',
        'Generating final report...'
    ];
    
    // Activate first step
    steps[0].classList.add('active');
    loadingStatus.textContent = messages[0];
    
    // Animate through steps
    window.loadingInterval = setInterval(() => {
        if (currentStep < steps.length) {
            steps[currentStep].classList.add('active');
            loadingStatus.textContent = messages[currentStep];
            currentStep++;
        } else {
            clearInterval(window.loadingInterval);
        }
    }, 15000); // Change step every 15 seconds
}

/**
 * Reset loading animation
 */
function resetLoadingAnimation() {
    if (window.loadingInterval) {
        clearInterval(window.loadingInterval);
    }
    [step1, step2, step3, step4].forEach(step => {
        step.classList.remove('active');
    });
}

// ============================================
// UI HELPERS
// ============================================

/**
 * Show a specific section, hide others
 */
function showSection(sectionToShow) {
    [inputSection, loadingSection, resultsSection].forEach(section => {
        section.classList.remove('active');
        section.style.display = 'none';
    });
    
    sectionToShow.classList.add('active');
    sectionToShow.style.display = 'block';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * Reset to input form
 */
function resetToForm() {
    ideaForm.reset();
    showSection(inputSection);
}

// ============================================
// INITIALIZATION
// ============================================

console.log('✅ Startup Idea Validator initialized');
console.log(`🌐 API URL: ${API_BASE_URL}`);

function goToDistribution() {
    if (!lastIdeaInput) {
        alert('No idea found. Please validate an idea first.');
        return;
    }

    const ideaText = `
Startup: ${lastIdeaInput.idea_name}

Problem:
${lastIdeaInput.problem}

Why this problem exists:
${lastIdeaInput.why_problem_exists}

Proposed Solution:
${lastIdeaInput.solution}

Target Audience:
${lastIdeaInput.target_audience}

Market / Industry:
${lastIdeaInput.market}

What makes it unique:
${lastIdeaInput.uniqueness}

Key Features:
${lastIdeaInput.key_features}

Revenue Model:
${lastIdeaInput.revenue_model}

Expected Users:
${lastIdeaInput.expected_users}

Region:
${lastIdeaInput.region}

Extra Notes:
${lastIdeaInput.extra_notes}
`.trim();

    const url = `${DISTRIBUTION_APP_URL}/?idea=${encodeURIComponent(ideaText)}`;
    window.location.href = url;
}