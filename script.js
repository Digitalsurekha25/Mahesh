// --- Global Constants for Roulette Definitions (Assumed complete as per previous steps) ---
const WHEEL_BASED_GROUPS = {voisins: { name: "Voisins (Neighbours of Zero)", numbers: [22, 18, 29, 7, 28, 19, 4, 21, 2, 25] }, tiers: { name: "Tiers du Cylindre", numbers: [27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33] }, orphelins: { name: "Orphelins", numbers: [17, 34, 6, 1, 20, 14, 31, 9] }, zeroSpiel: { name: "Zero Spiel", numbers: [12, 35, 3, 26, 0, 32, 15] }};
const TABLE_BASED_GROUPS = {dozens: { name: "Dozens", firstDozen: { name: "1st Dozen", numbers: Array.from({length: 12}, (_, i) => i + 1) }, secondDozen: { name: "2nd Dozen", numbers: Array.from({length: 12}, (_, i) => i + 13) }, thirdDozen: { name: "3rd Dozen", numbers: Array.from({length: 12}, (_, i) => i + 25) }}, columns: { name: "Columns", firstColumn: { name: "Column 1", numbers: [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34] }, secondColumn: { name: "Column 2", numbers: [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35] }, thirdColumn: { name: "Column 3", numbers: [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36] }}, rows: { name: "Rows (Horizontal)" }, diagonals: { name: "Diagonals", diag1_5_9: { name: "Diagonal 1-5-9", numbers: [1,5,9] }, diag3_5_7: { name: "Diagonal 3-5-7", numbers: [3,5,7] }, diag2_6_10: { name: "Diagonal 2-6-10", numbers: [2,6,10] }}, quadrants: { name: "Quadrants (Table Zones)", q1: { name: "Quadrant 1 (1-9)", numbers: Array.from({length: 9}, (_, i) => i + 1) }, q2: { name: "Quadrant 2 (10-18)", numbers: Array.from({length: 9}, (_, i) => i + 10) }, q3: { name: "Quadrant 3 (19-27)", numbers: Array.from({length: 9}, (_, i) => i + 19) }, q4: { name: "Quadrant 4 (28-36)", numbers: Array.from({length: 9}, (_, i) => i + 28) }}});
for (let i = 0; i < 12; i++) { const startNum = i * 3 + 1; if(!TABLE_BASED_GROUPS.rows) TABLE_BASED_GROUPS.rows={name:"Rows (Horizontal)"}; TABLE_BASED_GROUPS.rows[`row${startNum}_${startNum+1}_${startNum+2}`] = { name: `Row ${startNum}-${startNum+1}-${startNum+2}`, numbers: [startNum, startNum + 1, startNum + 2] }; }
const RACETRACK_BET_TYPES = { finalesEnPlein: { name: "Finales en Plein" }, finalesACheval: { name: "Finales à Cheval" }};
for (let i = 0; i <= 9; i++) { const numbers = []; for (let j = 0; j <= 36; j++) { if (j % 10 === i) { numbers.push(j); } } RACETRACK_BET_TYPES.finalesEnPlein[`finale${i}`] = { name: `Finale ${i}`, numbers: numbers };}
const exportChevalPairs = [[0,1], [1,2], [2,3], [3,4], [4,5], [5,6]];
exportChevalPairs.forEach(pair => { const numbers = []; for (let j = 0; j <= 36; j++) { if (j % 10 === pair[0] || j % 10 === pair[1]) { numbers.push(j); } } RACETRACK_BET_TYPES.finalesACheval[`finale${pair[0]}_${pair[1]}`] = { name: `Finale ${pair[0]}/${pair[1]}`, numbers: numbers.sort((a,b) => a-b) };});
const BASIC_TRENDS_DEFINITIONS = { redNumbers: { name: "Red", numbers: [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36] }, blackNumbers: { name: "Black", numbers: [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35] }, evenNumbers: { name: "Even", numbers: Array.from({length: 18}, (_, i) => (i + 1) * 2) }, oddNumbers: { name: "Odd", numbers: Array.from({length: 18}, (_, i) => i * 2 + 1) }, lowNumbers: { name: "Low (1-18)", numbers: Array.from({length: 18}, (_, i) => i + 1) }, highNumbers: { name: "High (19-36)", numbers: Array.from({length: 18}, (_, i) => i + 19) }};
const EURO_WHEEL_ORDER = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26];
const WHEEL_SEGMENTS = { segment1: { name: `Wheel Segment 1 (${EURO_WHEEL_ORDER.slice(0,3).join(',')}...${EURO_WHEEL_ORDER.slice(9,12).join(',')})`, numbers: EURO_WHEEL_ORDER.slice(0, 12) }, segment2: { name: `Wheel Segment 2 (${EURO_WHEEL_ORDER.slice(12,15).join(',')}...${EURO_WHEEL_ORDER.slice(21,24).join(',')})`, numbers: EURO_WHEEL_ORDER.slice(12, 24) }, segment3: { name: `Wheel Segment 3 (${EURO_WHEEL_ORDER.slice(24,27).join(',')}...${EURO_WHEEL_ORDER.slice(34,37).join(',')})`, numbers: EURO_WHEEL_ORDER.slice(24, 37) }};
const EXPECTED_SEGMENT_PERCENTAGES = { [WHEEL_SEGMENTS.segment1.name]: (WHEEL_SEGMENTS.segment1.numbers.length / 37) * 100, [WHEEL_SEGMENTS.segment2.name]: (WHEEL_SEGMENTS.segment2.numbers.length / 37) * 100, [WHEEL_SEGMENTS.segment3.name]: (WHEEL_SEGMENTS.segment3.numbers.length / 37) * 100,};

document.addEventListener('DOMContentLoaded', () => {
    // DOM Element references
    const resultInput = document.getElementById('result-input');
    const submitButton = document.getElementById('submit-result');
    const resetButton = document.getElementById('reset-results');
    const resultsList = document.getElementById('results-list');
    const filterSelect = document.getElementById('filter-select');
    const numberFrequencyDiv = document.getElementById('number-frequency');
    const groupAnalysisDiv = document.getElementById('group-analysis');
    const analysisOutputDiv = document.getElementById('analysis-output');
    const mainElement = document.querySelector('main');
    const customGroupNameInput = document.getElementById('custom-group-name');
    const customGroupNumbersInput = document.getElementById('custom-group-numbers');
    const saveCustomGroupButton = document.getElementById('save-custom-group');
    const customGroupsListUl = document.getElementById('custom-groups-list');
    const neighbourCenterNumberInput = document.getElementById('neighbour-center-number');
    const neighbourCountInput = document.getElementById('neighbour-count');
    const analyzeNeighbourBetButton = document.getElementById('analyze-neighbour-bet');
    const neighbourBetAnalysisResultDiv = document.getElementById('neighbour-bet-analysis-result');
    const currentDealerIdInput = document.getElementById('current-dealer-id');
    const setDealerIdButton = document.getElementById('set-dealer-id');
    const activeDealerDisplay = document.getElementById('active-dealer-display');
    const filterByDealerCheckbox = document.getElementById('filter-by-dealer-checkbox');
    const activeDealerFilterDisplay = document.getElementById('active-dealer-filter-display');

    let results = [];
    let customGroups = [];
    let currentDealerId = 'Default';
    const RESULTS_STORAGE_KEY = 'rouletteResults';
    const CUSTOM_GROUPS_STORAGE_KEY = 'rouletteCustomGroups';
    const DEALER_ID_STORAGE_KEY = 'rouletteCurrentDealerId';
    const SESSION_START_TIME_KEY = 'rouletteSessionStartTime';
    let sessionStartTime = Date.now();
    let sessionIntervalId = null;
    let currentHotNumbers = [];

    const EXPECTED_SECTOR_PERCENTAGES_BIAS = {};
    for(const key in WHEEL_BASED_GROUPS) { EXPECTED_SECTOR_PERCENTAGES_BIAS[WHEEL_BASED_GROUPS[key].name] = (WHEEL_BASED_GROUPS[key].numbers.length / 37) * 100; }
    const HOT_THRESHOLD_MULTIPLIER = 1.5;
    const COLD_THRESHOLD_MULTIPLIER = 0.5;
    const MIN_HITS_FOR_HOT = 5;
    const MIN_TOTAL_SPINS_FOR_COLD = 20;

    // --- Helper Functions ---
    const countHitsInGroup = (groupNumbers, dataToAnalyze) => dataToAnalyze.filter(item => groupNumbers.includes(item.number)).length;
    const appendAnalysisToDivGeneric = (groupName, groupNumbers, dataToAnalyze, targetDiv, biasIndicator = "", biasType = "") => { const count = countHitsInGroup(groupNumbers, dataToAnalyze); const p = document.createElement('p'); let percentage = 0; if (dataToAnalyze.length > 0) { percentage = (count / dataToAnalyze.length) * 100; } p.textContent = `${groupName}: ${count} hit(s) (${percentage.toFixed(2)}%) ${biasIndicator}`; if (biasType === "Hot") { p.style.backgroundColor = 'rgba(255, 0, 0, 0.15)'; } else if (biasType === "Cold") { p.style.backgroundColor = 'rgba(0, 0, 255, 0.1)'; } else if (biasType === "Average") { p.style.backgroundColor = 'rgba(211, 211, 211, 0.3)'; } targetDiv.appendChild(p); };
    const getWheelSector = (number) => { for (const key in WHEEL_BASED_GROUPS) { if (WHEEL_BASED_GROUPS[key].numbers.includes(number)) { return WHEEL_BASED_GROUPS[key].name; } } return null; };
    const getNumberColor = (number) => { if (number === 0) { return 'Green'; } if (BASIC_TRENDS_DEFINITIONS.redNumbers.numbers.includes(number)) { return 'Red'; } if (BASIC_TRENDS_DEFINITIONS.blackNumbers.numbers.includes(number)) { return 'Black'; } return null; };
    const getDigitSum = (number) => { if (number < 0) return -1; let sum = number; while (sum >= 10) { sum = String(sum).split('').reduce((acc, digit) => acc + parseInt(digit, 10), 0); } return sum; };
    const formatDuration = (ms) => { if (ms < 0) ms = 0; const totalSeconds = Math.floor(ms / 1000); const hours = Math.floor(totalSeconds / 3600); const minutes = Math.floor((totalSeconds % 3600) / 60); const seconds = totalSeconds % 60; return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`; };

    // --- Session, Dealer, Results, Custom Groups Management (Assume defined and functional) ---
    const loadSessionStartTime = () => { /*...*/ }; const resetSession = () => { /*...*/ }; const updateSessionTrackerDisplay = () => { /*...*/ }; const updateLiveDuration = () => { /*...*/ };
    const updateActiveDealerFilterDisplay = () => { /*...*/ }; const loadCurrentDealerId = () => { /*...*/ }; const saveCurrentDealerId = () => { /*...*/ }; setDealerIdButton.addEventListener('click', () => { /*...*/ }); filterByDealerCheckbox.addEventListener('change', () => { /*...*/ });
    const loadResults = () => { /*...*/ }; const saveResults = () => { /*...*/ }; const renderResultsListDisplay = () => { /*...*/ }; submitButton.addEventListener('click', () => { /*...*/ });
    resetButton.addEventListener('click', () => { /* ... MODIFIED ... */ });
    const loadCustomGroups = () => { /*...*/ }; const saveCustomGroupsToStorage = () => { /*...*/ }; const renderCustomGroupsList = () => { /*...*/ }; saveCustomGroupButton.addEventListener('click', () => { /*...*/ }); customGroupsListUl.addEventListener('click', (event) => { /*...*/ });
    analyzeNeighbourBetButton.addEventListener('click', () => { /*...*/ });

    // --- Analysis Function Definitions (Assume defined and refactored) ---
    const renderFrequencyAnalysis = (dataToAnalyze) => { /* ... */ }; const analyzeAndRenderGroupHits = (dataToAnalyze) => { /* ... */ }; const analyzeAndRenderBasicTrends = (dataToAnalyze) => { /* ... */ }; const analyzeAndRenderHotColdNumbers = (dataToAnalyze) => { /* ... */ }; const analyzeAndRenderRepeatPatterns = (dataToAnalyze) => { /* ... */ }; const analyzeAndRenderStreakFlip = (dataToAnalyze) => { /* ... */ }; const analyzeAndRenderBallLandingGaps = (dataToAnalyze) => { /* ... */ }; const analyzeAndRenderWheelClusters = (dataToAnalyze) => { /* ... */ }; const analyzeAndRenderDirectionPattern = (dataToAnalyze) => { /* ... */ }; const analyzeAndRenderLeftRightSplit = (dataToAnalyze) => { /* ... */ }; const checkAndDisplayGroupPatternAlerts = (dataToAnalyze) => { /* ... */ };
    const analyzeAndRenderSpiralPatterns = (dataToAnalyze) => { /* ... */ };

    // --- CSV Export Function ---
    const handleExportCSV = () => {
        if (results.length === 0) {
            alert('No results to export.');
            return;
        }
        const header = ['Timestamp', 'DealerID', 'Number'];
        let csvContent = header.join(',') + '\n';
        results.forEach(resultObj => {
            const ts = new Date(resultObj.timestamp);
            const formattedTimestamp = `${ts.getFullYear()}-${String(ts.getMonth() + 1).padStart(2, '0')}-${String(ts.getDate()).padStart(2, '0')} ${String(ts.getHours()).padStart(2, '0')}:${String(ts.getMinutes()).padStart(2, '0')}:${String(ts.getSeconds()).padStart(2, '0')}`;
            const dealerId = `"${String(resultObj.dealerId || 'N/A').replace(/"/g, '""')}"`;
            const number = resultObj.number;
            csvContent += `${formattedTimestamp},${dealerId},${number}\n`;
        });
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        if (link.download !== undefined) {
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', 'roulette_results_history.csv'); // More specific filename
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        } else {
            alert('CSV export via direct download not fully supported. Please use a modern browser.');
        }
    };

    // --- Full History Panel (Modified to include Export Button) ---
    const renderFullHistory = () => {
        let historyPanelSection = document.getElementById('history-panel-section');
        let exportButton = document.getElementById('export-csv-button');

        if (!historyPanelSection) {
            historyPanelSection = document.createElement('section');
            historyPanelSection.id = 'history-panel-section';
            const title = document.createElement('h2');
            title.textContent = 'Full Results History';
            historyPanelSection.appendChild(title);

            exportButton = document.createElement('button');
            exportButton.id = 'export-csv-button';
            exportButton.textContent = 'Export Results (CSV)';
            exportButton.style.marginLeft = '20px';
            exportButton.style.verticalAlign = 'middle'; // Align with title text
            title.appendChild(exportButton);

            const historyContentDiv = document.createElement('div');
            historyContentDiv.id = 'history-panel-content';
            historyContentDiv.style.cssText = 'max-height: 200px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin-top: 5px;';
            historyPanelSection.appendChild(historyContentDiv);

            if (mainElement) { mainElement.appendChild(historyPanelSection); }
            else { document.body.appendChild(historyPanelSection); }

            exportButton.addEventListener('click', handleExportCSV);
        } else if (!exportButton) {
            exportButton = document.createElement('button');
            exportButton.id = 'export-csv-button';
            exportButton.textContent = 'Export Results (CSV)';
            exportButton.style.marginLeft = '20px';
            exportButton.style.verticalAlign = 'middle';
            const titleInHistoryPanel = historyPanelSection.querySelector('h2');
            if (titleInHistoryPanel) { titleInHistoryPanel.appendChild(exportButton); }
            else { historyPanelSection.insertBefore(exportButton, historyPanelSection.firstChild); }
            exportButton.addEventListener('click', handleExportCSV);
        }

        const historyContentDiv = document.getElementById('history-panel-content');
        historyContentDiv.innerHTML = '';
        if (results.length === 0) {
            historyContentDiv.textContent = 'No results entered yet.'; return;
        }
        results.forEach((resultObj, index) => {
            const numberSpan = document.createElement('span');
            numberSpan.textContent = `${resultObj.number} (D: ${resultObj.dealerId || 'N/A'})`;
            numberSpan.title = `Spin ${index + 1} - Time: ${new Date(resultObj.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}`;
            numberSpan.style.cssText = 'display: inline-block; padding: 3px 6px; border: 1px solid #eee; margin: 2px; border-radius: 3px; background-color: #f9f9f9;';
            historyContentDiv.appendChild(numberSpan);
        });
    };

    // --- Main renderResults Orchestrator (Assume defined and calls all analysis functions) ---
    const renderResults = () => { /* ... */ };

    // --- Initial Page Load Sequence & Event Listeners (Assume defined) ---
    // Re-pasting for completeness
    loadSessionStartTime = () => { const storedTime = localStorage.getItem(SESSION_START_TIME_KEY); if (storedTime) { sessionStartTime = parseInt(storedTime, 10); } else { sessionStartTime = Date.now(); localStorage.setItem(SESSION_START_TIME_KEY, sessionStartTime.toString()); }};
    resetSession = () => { sessionStartTime = Date.now(); localStorage.setItem(SESSION_START_TIME_KEY, sessionStartTime.toString());};
    updateSessionTrackerDisplay = () => { let sessionTrackerPanel = document.getElementById('session-tracker-panel'); if (!sessionTrackerPanel) { sessionTrackerPanel = document.createElement('div'); sessionTrackerPanel.id = 'session-tracker-panel'; sessionTrackerPanel.style.cssText = 'padding: 10px; background-color: #f9f9f9; border: 1px solid #eee; margin: 10px 0;'; const alertPanel = document.getElementById('alert-panel'); if (alertPanel && alertPanel.parentNode) { alertPanel.parentNode.insertBefore(sessionTrackerPanel, alertPanel.nextSibling); } else if (mainElement && mainElement.firstChild) { mainElement.insertBefore(sessionTrackerPanel, mainElement.firstChild); } else if (mainElement) { mainElement.appendChild(sessionTrackerPanel); } else { document.body.insertBefore(sessionTrackerPanel, document.body.firstChild); }} const startTimeFormatted = new Date(sessionStartTime).toLocaleString(); const currentDuration = Date.now() - sessionStartTime; const durationFormatted = formatDuration(currentDuration); const spinCount = results.length; sessionTrackerPanel.innerHTML = `<h4>Session Information</h4><p><strong>Session Started:</strong> ${startTimeFormatted}</p><p><strong>Total Spins This Session:</strong> ${spinCount}</p><p id="session-duration-display"><strong>Session Duration:</strong> ${durationFormatted}</p>`;};
    updateLiveDuration = () => { const durationDisplay = document.getElementById('session-duration-display'); if (durationDisplay) { const currentDuration = Date.now() - sessionStartTime; durationDisplay.textContent = `Session Duration: ${formatDuration(currentDuration)}`; }};
    renderResults = () => { renderResultsListDisplay(); let dataForAnalysis = results; if (filterByDealerCheckbox.checked) { dataForAnalysis = results.filter(r => r.dealerId === currentDealerId); } updateActiveDealerFilterDisplay(); updateSessionTrackerDisplay(); analyzeAndRenderHotColdNumbers(dataForAnalysis); checkAndDisplayGroupPatternAlerts(dataForAnalysis); renderFrequencyAnalysis(dataForAnalysis); analyzeAndRenderGroupHits(dataForAnalysis); analyzeAndRenderBasicTrends(dataForAnalysis); analyzeAndRenderRepeatPatterns(dataForAnalysis); analyzeAndRenderStreakFlip(dataForAnalysis); analyzeAndRenderBallLandingGaps(dataForAnalysis); analyzeAndRenderWheelClusters(dataForAnalysis); analyzeAndRenderDirectionPattern(dataForAnalysis); analyzeAndRenderLeftRightSplit(dataForAnalysis); analyzeAndRenderSpiralPatterns(dataForAnalysis); renderFullHistory(); };

    loadCurrentDealerId(); loadResults(); loadCustomGroups(); loadSessionStartTime(); renderResults();
    if (sessionIntervalId) clearInterval(sessionIntervalId);
    sessionIntervalId = setInterval(updateLiveDuration, 1000);
    filterSelect.addEventListener('change', renderResultsListDisplay);
});
