// Configuration
const API_BASE = 'https://your-backend-api.herokuapp.com'; // Update this with your deployed backend URL
// For local development: const API_BASE = 'http://localhost:8000';

// Global state
let currentAnalysis = null;
let currentProtection = null;
let showMaskedText = false;
let sampleTexts = [];
let promptExamples = [];

// Initialize the application
async function initializeApp() {
    setupEventListeners();
    await checkApiHealth();
    await loadSampleTexts();
    await loadPromptExamples();
    setupPiiTypesLegend();
    showPage('main');
}

// Event listeners
function setupEventListeners() {
    // Character counters
    document.getElementById('inputText').addEventListener('input', function() {
        document.getElementById('charCount').textContent = this.value.length;
    });
    
    document.getElementById('promptInput').addEventListener('input', function() {
        document.getElementById('promptCharCount').textContent = this.value.length;
    });
}

// Page navigation
function showPage(page) {
    const mainPage = document.getElementById('mainPage');
    const protectPage = document.getElementById('protectPage');
    const mainBtn = document.getElementById('mainBtn');
    const protectBtn = document.getElementById('protectBtn');
    
    if (page === 'main') {
        mainPage.style.display = 'grid';
        protectPage.style.display = 'none';
        mainBtn.classList.add('bg-blue-600');
        mainBtn.classList.remove('bg-gray-400');
        protectBtn.classList.add('bg-gray-400');
        protectBtn.classList.remove('bg-green-600');
    } else {
        mainPage.style.display = 'none';
        protectPage.style.display = 'grid';
        protectBtn.classList.add('bg-green-600');
        protectBtn.classList.remove('bg-gray-400');
        mainBtn.classList.add('bg-gray-400');
        mainBtn.classList.remove('bg-blue-600');
    }
}

// API Health Check
async function checkApiHealth() {
    try {
        const response = await axios.get(`${API_BASE}/health`);
        const data = response.data;
        
        // Update API status
        const apiStatus = document.getElementById('apiStatus');
        apiStatus.innerHTML = `
            <div class="w-2 h-2 rounded-full mr-2 bg-green-500"></div>
            API ${data.status}
        `;
        apiStatus.className = 'flex items-center px-3 py-1 rounded-full bg-green-100 text-green-800';
        
        // Update model status
        const modelStatus = document.getElementById('modelStatus');
        modelStatus.innerHTML = `
            <i data-lucide="brain" class="w-3 h-3 mr-1"></i>
            ${data.model_type}
        `;
        modelStatus.className = 'flex items-center px-3 py-1 rounded-full bg-blue-100 text-blue-800';
        
        lucide.createIcons();
    } catch (error) {
        console.error('API health check failed:', error);
        
        // Update status to show offline
        const apiStatus = document.getElementById('apiStatus');
        apiStatus.innerHTML = `
            <div class="w-2 h-2 rounded-full mr-2 bg-red-500"></div>
            API Offline (Demo Mode)
        `;
        apiStatus.className = 'flex items-center px-3 py-1 rounded-full bg-red-100 text-red-800';
        
        // Show demo mode message
        showError('API is offline. Using demo mode with sample data.');
    }
}

// Load sample texts
async function loadSampleTexts() {
    try {
        const response = await axios.get(`${API_BASE}/demo/sample-texts`);
        sampleTexts = response.data.samples;
        
        const sampleButtons = document.getElementById('sampleButtons');
        sampleButtons.innerHTML = '';
        
        sampleTexts.forEach((sample, index) => {
            const button = document.createElement('button');
            button.className = 'px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors';
            button.textContent = sample.title;
            button.onclick = () => loadSampleText(sample);
            sampleButtons.appendChild(button);
        });
        
        document.getElementById('sampleTexts').style.display = 'block';
    } catch (error) {
        console.error('Failed to load sample texts:', error);
        // Use fallback sample texts
        sampleTexts = [
            {
                title: "Email Sample",
                text: "Hi John Smith, please contact me at john.doe@email.com or call 555-123-4567."
            },
            {
                title: "Business Card", 
                text: "Jane Wilson, CEO of TechCorp Inc. Email: jane@techcorp.com, Phone: (555) 987-6543."
            }
        ];
        
        const sampleButtons = document.getElementById('sampleButtons');
        sampleButtons.innerHTML = '';
        
        sampleTexts.forEach((sample) => {
            const button = document.createElement('button');
            button.className = 'px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors';
            button.textContent = sample.title;
            button.onclick = () => loadSampleText(sample);
            sampleButtons.appendChild(button);
        });
        
        document.getElementById('sampleTexts').style.display = 'block';
    }
}

// Load prompt examples
async function loadPromptExamples() {
    try {
        const response = await axios.get(`${API_BASE}/prompt-examples`);
        promptExamples = response.data.examples;
        
        const exampleButtons = document.getElementById('promptExampleButtons');
        exampleButtons.innerHTML = '';
        
        promptExamples.forEach((example) => {
            const button = document.createElement('button');
            button.className = 'p-3 text-left bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors';
            button.innerHTML = `
                <div class="font-medium text-sm text-gray-800">${example.category}</div>
                <div class="text-xs text-gray-600 mt-1 truncate">${example.original}</div>
                <div class="inline-flex items-center px-2 py-1 rounded-full text-xs mt-2 ${getRiskColorClass(example.risk_level)}">
                    ${example.risk_level} Risk
                </div>
            `;
            button.onclick = () => loadPromptExample(example);
            exampleButtons.appendChild(button);
        });
        
        document.getElementById('promptExamples').style.display = 'block';
    } catch (error) {
        console.error('Failed to load prompt examples:', error);
    }
}

// Setup PII types legend
function setupPiiTypesLegend() {
    const piiTypes = [
        'PERSON', 'EMAIL', 'PHONE', 'SSN', 'CREDIT_CARD',
        'ADDRESS', 'DATE', 'ORGANIZATION', 'LOCATION',
        'IP_ADDRESS', 'URL', 'BANK_ACCOUNT'
    ];
    
    const legend = document.getElementById('piiTypesLegend');
    legend.innerHTML = '';
    
    piiTypes.forEach(type => {
        const div = document.createElement('div');
        div.className = 'flex items-center';
        div.innerHTML = `
            <span class="px-2 py-1 rounded text-xs font-medium mr-2 ${getPiiTypeColor(type)}">
                ${type.replace('_', ' ')}
            </span>
        `;
        legend.appendChild(div);
    });
}

// Load sample text
function loadSampleText(sample) {
    document.getElementById('inputText').value = sample.text;
    document.getElementById('charCount').textContent = sample.text.length;
    clearResults();
}

// Load prompt example
function loadPromptExample(example) {
    document.getElementById('promptInput').value = example.original;
    document.getElementById('promptCharCount').textContent = example.original.length;
    clearPromptResults();
}

// Analyze text for PII
async function analyzeText() {
    const inputText = document.getElementById('inputText').value.trim();
    
    if (!inputText) {
        showError('Please enter some text to analyze');
        return;
    }
    
    setLoading('analyzeBtn', true);
    clearError();
    
    try {
        const response = await axios.post(`${API_BASE}/analyze`, {
            text: inputText
        });
        
        currentAnalysis = response.data;
        displayResults(currentAnalysis);
    } catch (error) {
        console.error('Analysis failed:', error);
        showError('Analysis failed. Please try again.');
        
        // Demo mode fallback
        currentAnalysis = createDemoAnalysis(inputText);
        displayResults(currentAnalysis);
    } finally {
        setLoading('analyzeBtn', false);
    }
}

// Protect prompt
async function protectPrompt() {
    const promptInput = document.getElementById('promptInput').value.trim();
    
    if (!promptInput) {
        showPromptError('Please enter a prompt to protect');
        return;
    }
    
    setLoading('protectBtn', true);
    clearPromptError();
    
    try {
        const showAlternatives = document.getElementById('showAlternatives').checked;
        
        const response = await axios.post(`${API_BASE}/protect-prompt`, {
            prompt: promptInput,
            num_alternatives: showAlternatives ? 3 : 0
        });
        
        currentProtection = response.data;
        displayPromptResults(currentProtection);
    } catch (error) {
        console.error('Prompt protection failed:', error);
        showPromptError('Prompt protection failed. Please try again.');
        
        // Demo mode fallback
        currentProtection = createDemoProtection(promptInput);
        displayPromptResults(currentProtection);
    } finally {
        setLoading('protectBtn', false);
    }
}

// Display analysis results
function displayResults(analysis) {
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
    
    // Update statistics
    document.getElementById('piiCount').textContent = analysis.pii_count;
    document.getElementById('piiTypes').textContent = analysis.pii_types.length;
    
    // Display text
    updateDisplayText();
    
    // Show detected entities
    if (analysis.detected_entities.length > 0) {
        displayDetectedEntities(analysis.detected_entities);
        document.getElementById('entitiesSidebar').style.display = 'block';
    }
}

// Display prompt protection results
function displayPromptResults(protection) {
    // Show results section
    document.getElementById('promptResults').style.display = 'block';
    
    // Update risk badge
    const riskBadge = document.getElementById('riskBadge');
    riskBadge.className = `inline-flex items-center px-3 py-1 rounded-full text-sm ${getRiskColorClass(protection.risk_level)}`;
    riskBadge.textContent = `${protection.risk_level} Risk`;
    
    // Display prompts
    document.getElementById('originalPrompt').textContent = protection.original_prompt;
    document.getElementById('protectedPrompt').textContent = protection.protected_prompt;
    
    // Display alternatives
    if (protection.alternatives && protection.alternatives.length > 0) {
        displayAlternatives(protection.alternatives);
        document.getElementById('alternativesSection').style.display = 'block';
    }
    
    // Update statistics
    document.getElementById('promptPiiCount').textContent = protection.pii_count;
    document.getElementById('promptPiiTypes').textContent = protection.pii_types.length;
    document.getElementById('promptContext').textContent = protection.context;
    
    // Show suggestions
    if (protection.suggestions && protection.suggestions.length > 0) {
        displaySuggestions(protection.suggestions);
        document.getElementById('suggestionsSidebar').style.display = 'block';
    }
}

// Update display text (original or masked)
function updateDisplayText() {
    if (!currentAnalysis) return;
    
    const displayText = document.getElementById('displayText');
    const textLabel = document.getElementById('textLabel');
    const toggleBtn = document.getElementById('toggleBtn');
    
    if (showMaskedText) {
        displayText.textContent = currentAnalysis.masked_text;
        textLabel.innerHTML = '<i data-lucide="lock" class="w-4 h-4 mr-2 text-red-600"></i>Masked Text (Safe for AI)';
        toggleBtn.innerHTML = '<i data-lucide="eye-off" class="w-4 h-4 mr-1"></i>Show Original';
    } else {
        displayText.innerHTML = highlightPII(currentAnalysis.original_text, currentAnalysis.detected_entities);
        textLabel.innerHTML = '<i data-lucide="unlock" class="w-4 h-4 mr-2 text-green-600"></i>Original Text with PII Highlighted';
        toggleBtn.innerHTML = '<i data-lucide="eye" class="w-4 h-4 mr-1"></i>Show Masked';
    }
    
    lucide.createIcons();
}

// Toggle between original and masked text
function toggleMasked() {
    showMaskedText = !showMaskedText;
    updateDisplayText();
}

// Highlight PII in text
function highlightPII(text, entities) {
    if (!entities.length) return text;
    
    let highlightedText = text;
    const sortedEntities = [...entities].sort((a, b) => b.text.length - a.text.length);
    
    sortedEntities.forEach(entity => {
        const regex = new RegExp(`\\b${entity.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'g');
        highlightedText = highlightedText.replace(
            regex,
            `<span class="pii-highlight pii-${entity.type}" title="${entity.type} (${(entity.confidence * 100).toFixed(1)}% confidence)">${entity.text}</span>`
        );
    });
    
    return highlightedText;
}

// Display detected entities
function displayDetectedEntities(entities) {
    const entitiesList = document.getElementById('entitiesList');
    entitiesList.innerHTML = '';
    
    entities.forEach(entity => {
        const div = document.createElement('div');
        div.className = 'border-l-4 border-blue-500 pl-3';
        div.innerHTML = `
            <div class="font-medium text-sm">${entity.text}</div>
            <div class="flex items-center justify-between text-xs text-gray-600">
                <span class="px-2 py-1 rounded ${getPiiTypeColor(entity.type)}">
                    ${entity.type.replace('_', ' ')}
                </span>
                <span>${(entity.confidence * 100).toFixed(1)}%</span>
            </div>
        `;
        entitiesList.appendChild(div);
    });
}

// Display alternatives
function displayAlternatives(alternatives) {
    const alternativesList = document.getElementById('alternativesList');
    alternativesList.innerHTML = '';
    
    alternatives.forEach((alt, index) => {
        const div = document.createElement('div');
        div.className = 'p-3 bg-blue-50 rounded-lg';
        div.innerHTML = `
            <div class="flex items-center justify-between mb-1">
                <span class="text-sm font-medium text-blue-800">Alternative ${index + 1}</span>
                <button onclick="copyToClipboard('alt-${index}')" class="p-1 text-blue-600 hover:text-blue-800">
                    <i data-lucide="copy" class="w-4 h-4"></i>
                </button>
            </div>
            <div id="alt-${index}" class="text-sm text-blue-700">${alt}</div>
        `;
        alternativesList.appendChild(div);
    });
    
    lucide.createIcons();
}

// Display suggestions
function displaySuggestions(suggestions) {
    const suggestionsList = document.getElementById('suggestionsList');
    suggestionsList.innerHTML = '';
    
    suggestions.forEach(suggestion => {
        const div = document.createElement('div');
        div.className = 'p-3 bg-yellow-50 rounded-lg';
        div.innerHTML = `<div class="text-sm text-yellow-800">${suggestion}</div>`;
        suggestionsList.appendChild(div);
    });
}

// Utility functions
function getPiiTypeColor(type) {
    const colors = {
        'PERSON': 'bg-blue-100 text-blue-800',
        'EMAIL': 'bg-green-100 text-green-800',
        'PHONE': 'bg-purple-100 text-purple-800',
        'SSN': 'bg-red-100 text-red-800',
        'CREDIT_CARD': 'bg-orange-100 text-orange-800',
        'ADDRESS': 'bg-indigo-100 text-indigo-800',
        'DATE': 'bg-pink-100 text-pink-800',
        'ORGANIZATION': 'bg-teal-100 text-teal-800',
        'LOCATION': 'bg-cyan-100 text-cyan-800',
        'IP_ADDRESS': 'bg-gray-100 text-gray-800',
        'URL': 'bg-lime-100 text-lime-800',
        'BANK_ACCOUNT': 'bg-amber-100 text-amber-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
}

function getRiskColorClass(riskLevel) {
    switch (riskLevel) {
        case 'HIGH': return 'text-red-600 bg-red-100';
        case 'MEDIUM': return 'text-yellow-600 bg-yellow-100';
        case 'LOW': return 'text-green-600 bg-green-100';
        default: return 'text-gray-600 bg-gray-100';
    }
}

function setLoading(buttonId, loading) {
    const button = document.getElementById(buttonId);
    if (loading) {
        button.disabled = true;
        button.innerHTML = `
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            Processing...
        `;
    } else {
        button.disabled = false;
        if (buttonId === 'analyzeBtn') {
            button.innerHTML = '<i data-lucide="brain" class="w-4 h-4 mr-2"></i>Analyze PII';
        } else if (buttonId === 'protectBtn') {
            button.innerHTML = '<i data-lucide="shield" class="w-4 h-4 mr-2"></i>Protect Prompt';
        }
        lucide.createIcons();
    }
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function clearError() {
    document.getElementById('errorMessage').style.display = 'none';
}

function showPromptError(message) {
    const errorDiv = document.getElementById('promptError');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function clearPromptError() {
    document.getElementById('promptError').style.display = 'none';
}

function clearResults() {
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('entitiesSidebar').style.display = 'none';
    currentAnalysis = null;
    showMaskedText = false;
}

function clearPromptResults() {
    document.getElementById('promptResults').style.display = 'none';
    document.getElementById('suggestionsSidebar').style.display = 'none';
    document.getElementById('alternativesSection').style.display = 'none';
    currentProtection = null;
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const text = element.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        // Show temporary success message
        const originalText = element.innerHTML;
        element.innerHTML = '<span class="text-green-600">Copied!</span>';
        setTimeout(() => {
            element.innerHTML = originalText;
        }, 1000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}

// Demo mode fallbacks
function createDemoAnalysis(text) {
    // Simple demo analysis for offline mode
    const entities = [];
    
    // Basic email detection
    const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
    let match;
    while ((match = emailRegex.exec(text)) !== null) {
        entities.push({
            text: match[0],
            type: 'EMAIL',
            confidence: 0.9
        });
    }
    
    // Basic phone detection
    const phoneRegex = /\b\d{3}-\d{3}-\d{4}\b/g;
    while ((match = phoneRegex.exec(text)) !== null) {
        entities.push({
            text: match[0],
            type: 'PHONE',
            confidence: 0.9
        });
    }
    
    // Create masked text
    let maskedText = text;
    entities.forEach((entity, index) => {
        maskedText = maskedText.replace(entity.text, `[${entity.type}_demo${index}]`);
    });
    
    return {
        original_text: text,
        masked_text: maskedText,
        detected_entities: entities,
        pii_count: entities.length,
        pii_types: [...new Set(entities.map(e => e.type))],
        mask_info: []
    };
}

function createDemoProtection(prompt) {
    // Simple demo protection for offline mode
    const analysis = createDemoAnalysis(prompt);
    
    return {
        original_prompt: prompt,
        protected_prompt: analysis.masked_text,
        protection_applied: analysis.pii_count > 0,
        detected_pii: analysis.detected_entities,
        replacements_made: [],
        suggestions: ['This is demo mode. Connect to API for full functionality.'],
        context: 'general',
        risk_level: analysis.pii_count > 0 ? 'MEDIUM' : 'LOW',
        pii_count: analysis.pii_count,
        pii_types: analysis.pii_types,
        alternatives: []
    };
}