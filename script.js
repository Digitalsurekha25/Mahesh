// WHEEL-BASED GROUPS (SECTORS) - As per FINAL MASTER LIST
const WHEEL_BASED_GROUPS = {
    voisins: {
        name: "Voisins (Neighbours of Zero)",
        numbers: [22, 18, 29, 7, 28, 19, 4, 21, 2, 25]
    },
    tiers: {
        name: "Tiers du Cylindre",
        numbers: [27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33]
    },
    orphelins: {
        name: "Orphelins",
        numbers: [17, 34, 6, 1, 20, 14, 31, 9]
    },
    zeroSpiel: {
        name: "Zero Spiel",
        numbers: [12, 35, 3, 26, 0, 32, 15]
    }
};

// TABLE-BASED GROUPS (LAYOUT CLUSTERS) - As per FINAL MASTER LIST
const TABLE_BASED_GROUPS = {
    dozens: {
        name: "Dozens",
        firstDozen: {
            name: "1st Dozen",
            numbers: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        },
        secondDozen: {
            name: "2nd Dozen",
            numbers: [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        },
        thirdDozen: {
            name: "3rd Dozen",
            numbers: [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
        }
    },
    columns: {
        name: "Columns",
        firstColumn: {
            name: "Column 1",
            numbers: [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
        },
        secondColumn: {
            name: "Column 2",
            numbers: [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35]
        },
        thirdColumn: {
            name: "Column 3",
            numbers: [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
        }
    },
    rows: {
        name: "Rows (Horizontal)"
    },
    diagonals: {
        name: "Diagonals",
        diag1_5_9: { name: "Diagonal 1-5-9", numbers: [1,5,9] },
        diag3_5_7: { name: "Diagonal 3-5-7", numbers: [3,5,7] },
        diag2_6_10: { name: "Diagonal 2-6-10", numbers: [2,6,10] }
    },
    quadrants: {
        name: "Quadrants (Table Zones)",
        q1: { name: "Quadrant 1 (1-9)", numbers: [1,2,3,4,5,6,7,8,9] },
        q2: { name: "Quadrant 2 (10-18)", numbers: [10,11,12,13,14,15,16,17,18] },
        q3: { name: "Quadrant 3 (19-27)", numbers: [19,20,21,22,23,24,25,26,27] },
        q4: { name: "Quadrant 4 (28-36)", numbers: [28,29,30,31,32,33,34,35,36] }
    }
};

for (let i = 0; i < 12; i++) {
    const startNum = i * 3 + 1;
    TABLE_BASED_GROUPS.rows[`row${startNum}_${startNum+1}_${startNum+2}`] = {
        name: `Row ${startNum}-${startNum+1}-${startNum+2}`,
        numbers: [startNum, startNum + 1, startNum + 2]
    };
}

const RACETRACK_BET_TYPES = {
    finalesEnPlein: {
        name: "Finales en Plein",
    },
    finalesACheval: {
        name: "Finales à Cheval",
    }
};

for (let i = 0; i <= 9; i++) {
    const numbers = [];
    for (let j = 0; j <= 36; j++) {
        if (j % 10 === i) {
            numbers.push(j);
        }
    }
    RACETRACK_BET_TYPES.finalesEnPlein[`finale${i}`] = {
        name: `Finale ${i}`,
        numbers: numbers
    };
}

const chevalPairs = [[0,1], [1,2], [2,3], [3,4], [4,5], [5,6]];
chevalPairs.forEach(pair => {
    const numbers = [];
    for (let j = 0; j <= 36; j++) {
        if (j % 10 === pair[0] || j % 10 === pair[1]) {
            numbers.push(j);
        }
    }
    RACETRACK_BET_TYPES.finalesACheval[`finale${pair[0]}_${pair[1]}`] = {
        name: `Finale ${pair[0]}/${pair[1]}`,
        numbers: numbers.sort((a,b) => a-b)
    };
});

const BASIC_TRENDS_DEFINITIONS = {
    redNumbers: {
        name: "Red",
        numbers: [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
    },
    blackNumbers: {
        name: "Black",
        numbers: [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    },
    evenNumbers: {
        name: "Even",
        numbers: [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36]
    },
    oddNumbers: {
        name: "Odd",
        numbers: [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35]
    },
    lowNumbers: {
        name: "Low (1-18)",
        numbers: Array.from({length: 18}, (_, i) => i + 1)
    },
    highNumbers: {
        name: "High (19-36)",
        numbers: Array.from({length: 18}, (_, i) => i + 19)
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const resultInput = document.getElementById('result-input');
    const submitButton = document.getElementById('submit-result');
    const resetButton = document.getElementById('reset-results');
    const resultsList = document.getElementById('results-list');
    const filterSelect = document.getElementById('filter-select');
    const numberFrequencyDiv = document.getElementById('number-frequency');
    const groupAnalysisDiv = document.getElementById('group-analysis');
    const analysisOutputDiv = document.getElementById('analysis-output');

    let results = [];

    const calculateFrequency = (allResults) => {
        const counts = {};
        for (let i = 0; i <= 36; i++) {
            counts[i.toString()] = 0;
        }
        allResults.forEach(result => {
            counts[result.toString()]++;
        });
        return counts;
    };

    const renderFrequencyAnalysis = () => {
        numberFrequencyDiv.innerHTML = '<h3>Number Frequency</h3>';
        if (results.length === 0) {
            const p = document.createElement('p');
            p.textContent = 'No results entered yet.';
            numberFrequencyDiv.appendChild(p);
            return;
        }
        const totalResultsP = document.createElement('p');
        totalResultsP.textContent = `Total Results: ${results.length}`;
        numberFrequencyDiv.appendChild(totalResultsP);
        const frequencies = calculateFrequency(results);
        for (let i = 0; i <= 36; i++) {
            const numKey = i.toString();
            if (frequencies[numKey] > 0) {
                const percentage = (frequencies[numKey] / results.length) * 100;
                const p = document.createElement('p');
                p.textContent = `Number ${i}: ${frequencies[numKey]} hit(s) (${percentage.toFixed(2)}%)`;
                numberFrequencyDiv.appendChild(p);
            }
        }
    };

    const appendAnalysisToDivGeneric = (groupName, groupNumbers, allResults, targetDiv) => {
        const countHitsInGroup = (numbersToCount, sourceResults) => {
            return sourceResults.filter(num => numbersToCount.includes(num)).length;
        };
        const count = countHitsInGroup(groupNumbers, allResults);
        if (allResults.length > 0) {
            const percentage = (count / allResults.length) * 100;
            const p = document.createElement('p');
            p.textContent = `${groupName}: ${count} hit(s) (${percentage.toFixed(2)}%)`;
            targetDiv.appendChild(p);
        }
    };

    const analyzeAndRenderGroupHits = () => {
        groupAnalysisDiv.innerHTML = '<h3>Group Hit Frequency</h3>';
        if (results.length === 0) {
            const p = document.createElement('p');
            p.textContent = 'No results entered yet for group analysis.';
            groupAnalysisDiv.appendChild(p);
            return;
        }
        let sectionTitle;

        sectionTitle = document.createElement('h4');
        sectionTitle.textContent = 'Wheel Sectors';
        groupAnalysisDiv.appendChild(sectionTitle);
        for (const key in WHEEL_BASED_GROUPS) {
            const group = WHEEL_BASED_GROUPS[key];
            appendAnalysisToDivGeneric(group.name, group.numbers, results, groupAnalysisDiv);
        }
        groupAnalysisDiv.appendChild(document.createElement('hr'));

        sectionTitle = document.createElement('h4');
        sectionTitle.textContent = TABLE_BASED_GROUPS.dozens.name;
        groupAnalysisDiv.appendChild(sectionTitle);
        for (const key in TABLE_BASED_GROUPS.dozens) {
            if (key === 'name') continue;
            const dozen = TABLE_BASED_GROUPS.dozens[key];
            appendAnalysisToDivGeneric(dozen.name, dozen.numbers, results, groupAnalysisDiv);
        }
        groupAnalysisDiv.appendChild(document.createElement('hr'));

        sectionTitle = document.createElement('h4');
        sectionTitle.textContent = TABLE_BASED_GROUPS.columns.name;
        groupAnalysisDiv.appendChild(sectionTitle);
        for (const key in TABLE_BASED_GROUPS.columns) {
            if (key === 'name') continue;
            const column = TABLE_BASED_GROUPS.columns[key];
            appendAnalysisToDivGeneric(column.name, column.numbers, results, groupAnalysisDiv);
        }
        groupAnalysisDiv.appendChild(document.createElement('hr'));

        sectionTitle = document.createElement('h4');
        sectionTitle.textContent = TABLE_BASED_GROUPS.rows.name;
        groupAnalysisDiv.appendChild(sectionTitle);
        for (const key in TABLE_BASED_GROUPS.rows) {
            if (key === 'name') continue;
            const row = TABLE_BASED_GROUPS.rows[key];
            appendAnalysisToDivGeneric(row.name, row.numbers, results, groupAnalysisDiv);
        }
        groupAnalysisDiv.appendChild(document.createElement('hr'));

        sectionTitle = document.createElement('h4');
        sectionTitle.textContent = TABLE_BASED_GROUPS.diagonals.name;
        groupAnalysisDiv.appendChild(sectionTitle);
        for (const key in TABLE_BASED_GROUPS.diagonals) {
            if (key === 'name') continue;
            const diagonal = TABLE_BASED_GROUPS.diagonals[key];
            appendAnalysisToDivGeneric(diagonal.name, diagonal.numbers, results, groupAnalysisDiv);
        }
        groupAnalysisDiv.appendChild(document.createElement('hr'));

        sectionTitle = document.createElement('h4');
        sectionTitle.textContent = TABLE_BASED_GROUPS.quadrants.name;
        groupAnalysisDiv.appendChild(sectionTitle);
        for (const key in TABLE_BASED_GROUPS.quadrants) {
            if (key === 'name') continue;
            const quadrant = TABLE_BASED_GROUPS.quadrants[key];
            appendAnalysisToDivGeneric(quadrant.name, quadrant.numbers, results, groupAnalysisDiv);
        }
        groupAnalysisDiv.appendChild(document.createElement('hr'));

        sectionTitle = document.createElement('h4');
        sectionTitle.textContent = RACETRACK_BET_TYPES.finalesEnPlein.name;
        groupAnalysisDiv.appendChild(sectionTitle);
        for (const key in RACETRACK_BET_TYPES.finalesEnPlein) {
            if (key === 'name') continue;
            const finale = RACETRACK_BET_TYPES.finalesEnPlein[key];
            if(finale.numbers.length > 0) {
                 appendAnalysisToDivGeneric(finale.name, finale.numbers, results, groupAnalysisDiv);
            }
        }
        groupAnalysisDiv.appendChild(document.createElement('hr'));

        sectionTitle = document.createElement('h4');
        sectionTitle.textContent = RACETRACK_BET_TYPES.finalesACheval.name;
        groupAnalysisDiv.appendChild(sectionTitle);
        for (const key in RACETRACK_BET_TYPES.finalesACheval) {
            if (key === 'name') continue;
            const finaleCheval = RACETRACK_BET_TYPES.finalesACheval[key];
            if(finaleCheval.numbers.length > 0) {
                appendAnalysisToDivGeneric(finaleCheval.name, finaleCheval.numbers, results, groupAnalysisDiv);
            }
        }
    };

    const analyzeAndRenderBasicTrends = () => {
        let basicTrendsDiv = document.getElementById('basic-trends-analysis');
        if (!basicTrendsDiv) {
            basicTrendsDiv = document.createElement('div');
            basicTrendsDiv.id = 'basic-trends-analysis';
            const groupAnalysisElement = document.getElementById('group-analysis');
            if (groupAnalysisElement && groupAnalysisElement.parentNode === analysisOutputDiv) {
                 analysisOutputDiv.insertBefore(basicTrendsDiv, groupAnalysisElement.nextSibling);
            } else {
                 analysisOutputDiv.appendChild(basicTrendsDiv);
            }
        }
        basicTrendsDiv.innerHTML = '<h3>Basic Trends (Even/Odd, Red/Black, Low/High)</h3>';
        if (results.length === 0) {
            const p = document.createElement('p');
            p.textContent = 'No results entered yet for basic trend analysis.';
            basicTrendsDiv.appendChild(p);
            return;
        }
        const appendTrendToDiv = (trendName, trendNumbers, allResults, targetDiv) => {
            const relevantResults = allResults.filter(num => num !== 0);
            if (relevantResults.length === 0) {
                const p = document.createElement('p');
                if (allResults.length > 0 && allResults.every(num => num === 0)) {
                     p.textContent = `${trendName}: N/A (only zero(s) entered)`;
                } else {
                     p.textContent = `${trendName}: 0 hit(s) (0.00%) of non-zero numbers`;
                }
                targetDiv.appendChild(p);
                return;
            }
            const count = relevantResults.filter(num => trendNumbers.includes(num)).length;
            const percentage = (count / relevantResults.length) * 100;
            const p = document.createElement('p');
            p.textContent = `${trendName}: ${count} hit(s) (${percentage.toFixed(2)}%) of ${relevantResults.length} non-zero results`;
            targetDiv.appendChild(p);
        };
        appendTrendToDiv(BASIC_TRENDS_DEFINITIONS.redNumbers.name, BASIC_TRENDS_DEFINITIONS.redNumbers.numbers, results, basicTrendsDiv);
        appendTrendToDiv(BASIC_TRENDS_DEFINITIONS.blackNumbers.name, BASIC_TRENDS_DEFINITIONS.blackNumbers.numbers, results, basicTrendsDiv);
        basicTrendsDiv.appendChild(document.createElement('hr'));
        appendTrendToDiv(BASIC_TRENDS_DEFINITIONS.evenNumbers.name, BASIC_TRENDS_DEFINITIONS.evenNumbers.numbers, results, basicTrendsDiv);
        appendTrendToDiv(BASIC_TRENDS_DEFINITIONS.oddNumbers.name, BASIC_TRENDS_DEFINITIONS.oddNumbers.numbers, results, basicTrendsDiv);
        basicTrendsDiv.appendChild(document.createElement('hr'));
        appendTrendToDiv(BASIC_TRENDS_DEFINITIONS.lowNumbers.name, BASIC_TRENDS_DEFINITIONS.lowNumbers.numbers, results, basicTrendsDiv);
        appendTrendToDiv(BASIC_TRENDS_DEFINITIONS.highNumbers.name, BASIC_TRENDS_DEFINITIONS.highNumbers.numbers, results, basicTrendsDiv);
    };

    const analyzeAndRenderHotColdNumbers = () => {
        let hotColdDiv = document.getElementById('hot-cold-analysis');
        if (!hotColdDiv) {
            hotColdDiv = document.createElement('div');
            hotColdDiv.id = 'hot-cold-analysis';
            const basicTrendsAnalysisDiv = document.getElementById('basic-trends-analysis'); // Corrected ID
            if (basicTrendsAnalysisDiv && basicTrendsAnalysisDiv.parentNode === analysisOutputDiv) {
                analysisOutputDiv.insertBefore(hotColdDiv, basicTrendsAnalysisDiv.nextSibling);
            } else {
                analysisOutputDiv.appendChild(hotColdDiv); // Fallback
            }
        }

        const filterValue = filterSelect.value;
        let currentRangeResults = results;
        let titleRangeText = "All";

        if (filterValue !== 'all') {
            const count = parseInt(filterValue, 10);
            // Ensure we don't try to slice more than available, though slice handles this gracefully.
            currentRangeResults = results.slice(-Math.min(count, results.length));
            titleRangeText = `Last ${currentRangeResults.length}`; // Reflect actual number of results if less than count
        } else {
            titleRangeText = `All (${results.length})`;
        }

        hotColdDiv.innerHTML = `<h3>Hot & Cold Numbers (${titleRangeText} Results)</h3>`;

        if (currentRangeResults.length === 0) {
            const p = document.createElement('p');
            p.textContent = 'No results in the selected range for Hot/Cold analysis.';
            hotColdDiv.appendChild(p);
            return;
        }

        const frequencies = {};
        for (let i = 0; i <= 36; i++) {
            frequencies[i] = { number: i, count: 0 };
        }

        currentRangeResults.forEach(num => {
            frequencies[num].count++;
        });

        const allNumbersByFreq = Object.values(frequencies).sort((a, b) => {
            if (b.count === a.count) {
                return a.number - b.number;
            }
            return b.count - a.count;
        });

        const hotNumbersOutput = allNumbersByFreq.filter(item => item.count > 0).slice(0, 5);
        const hotNumbersP = document.createElement('p');
        hotNumbersP.innerHTML = '<strong>Hot Numbers:</strong> ';
        if (hotNumbersOutput.length > 0) {
            hotNumbersOutput.forEach((item, index) => {
                hotNumbersP.innerHTML += `${item.number} (${item.count} hit${item.count > 1 ? 's' : ''})${index < hotNumbersOutput.length - 1 ? ', ' : ''}`;
            });
        } else {
            hotNumbersP.innerHTML += 'N/A (no numbers have appeared in this range)';
        }
        hotColdDiv.appendChild(hotNumbersP);

        const coldCandidates = Object.values(frequencies).sort((a,b) => {
            if (a.count === b.count) {
                return a.number - b.number;
            }
            return a.count - b.count;
        });

        const coldNumbersOutput = coldCandidates.slice(0, 5);
        const coldNumbersP = document.createElement('p');
        coldNumbersP.innerHTML = '<strong>Cold Numbers:</strong> ';
         if (coldNumbersOutput.length > 0) {
            coldNumbersOutput.forEach((item, index) => {
                coldNumbersP.innerHTML += `${item.number} (${item.count} hit${item.count > 1 ? 's' : ''})${index < coldNumbersOutput.length - 1 ? ', ' : ''}`;
            });
        } else {
             // This case should ideally not be hit if frequencies for 0-36 are always initialized.
            coldNumbersP.innerHTML += 'N/A';
        }
        hotColdDiv.appendChild(coldNumbersP);
    };

    const loadResults = () => {
        const storedResults = localStorage.getItem('rouletteResults');
        if (storedResults) {
            results = JSON.parse(storedResults);
            results = results.map(r => parseInt(r, 10));
        }
        renderResults();
    };

    const renderResults = () => {
        resultsList.innerHTML = '';
        const filterValue = filterSelect.value;
        let resultsToDisplay = results;
        if (filterValue !== 'all') {
            const count = parseInt(filterValue, 10);
            resultsToDisplay = results.slice(-count);
        }
        resultsToDisplay.forEach(result => {
            const listItem = document.createElement('li');
            listItem.textContent = result;
            resultsList.appendChild(listItem);
        });
        renderFrequencyAnalysis();
        analyzeAndRenderGroupHits();
        analyzeAndRenderBasicTrends();
        analyzeAndRenderHotColdNumbers(); // Added call
    };

    const saveResults = () => {
        localStorage.setItem('rouletteResults', JSON.stringify(results));
    };

    submitButton.addEventListener('click', () => {
        const inputValue = resultInput.value.trim();
        if (inputValue === '') {
            alert('Please enter a number.');
            return;
        }
        const number = parseInt(inputValue, 10);
        if (isNaN(number) || number < 0 || number > 36) {
            alert('Invalid input. Please enter a number between 0 and 36.');
            resultInput.value = '';
            return;
        }
        results.push(number);
        saveResults();
        renderResults();
        resultInput.value = '';
    });

    resetButton.addEventListener('click', () => {
        if (confirm('Are you sure you want to reset all results?')) {
            results = [];
            saveResults();
            renderResults();
        }
    });

    filterSelect.addEventListener('change', () => {
        renderResults(); // This will now also update Hot/Cold numbers based on the new filter
    });

    loadResults();
});
