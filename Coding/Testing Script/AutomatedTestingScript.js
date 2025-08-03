// ==- KODE OTOMISASI PENGUJIAN WEBSITE -==
// VERSI 3.1 - Dengan Parser CSV yang Diperbaiki
// Petunjuk:
// 1. Salin dan tempel kode ini ke dalam Developer Console. Tekan Enter.
// 2. Dua tombol baru akan muncul di bagian atas halaman: "Load Test CSV" dan "Start Testing".
// 3. Klik "Load Test CSV" dan pilih file `persona_test_cases.csv` Anda.
// 4. Setelah file dimuat, klik "Start Testing" untuk memulai proses.
// 5. Hasilnya akan diunduh sebagai file CSV setelah selesai.

(function() {

    // --- UI Injection ---
    // Membuat container untuk tombol-tombol
    const controlContainer = document.createElement('div');
    controlContainer.style.position = 'fixed';
    controlContainer.style.top = '10px';
    controlContainer.style.right = '10px';
    controlContainer.style.zIndex = '9999';
    controlContainer.style.backgroundColor = 'white';
    controlContainer.style.border = '1px solid #ccc';
    controlContainer.style.padding = '10px';
    controlContainer.style.borderRadius = '5px';
    controlContainer.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
    controlContainer.innerHTML = `
        <h4 style="margin: 0 0 10px 0; font-family: sans-serif; font-size: 16px;">Test Automation</h4>
        <input type="file" id="csvFileInput" accept=".csv" style="display: block; margin-bottom: 10px;">
        <button id="startTestBtn" style="width: 100%; padding: 8px; cursor: pointer;">Start Testing</button>
        <div id="statusArea" style="margin-top: 10px; font-family: sans-serif; font-size: 12px;">Status: Waiting for file...</div>
    `;
    document.body.appendChild(controlContainer);
    
    let testCases = []; // Array ini akan diisi dari file CSV

    const fileInput = document.getElementById('csvFileInput');
    const startBtn = document.getElementById('startTestBtn');
    const statusArea = document.getElementById('statusArea');

    fileInput.addEventListener('change', handleFileSelect, false);
    startBtn.addEventListener('click', runAutomation, false);
    
    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) {
            statusArea.textContent = "No file selected.";
            return;
        }
        const reader = new FileReader();
        reader.onload = function(e) {
            const text = e.target.result;
            try {
                testCases = parseCSV(text);
                statusArea.textContent = `${testCases.length} test cases loaded successfully.`;
                console.log(`${testCases.length} test cases loaded.`);
            } catch(error) {
                statusArea.textContent = `Error parsing CSV: ${error.message}`;
                console.error(error);
            }
        };
        reader.readAsText(file);
    }

    // *** PERBAIKAN PARSER CSV DI SINI ***
    function parseCSV(text) {
        const lines = text.split('\n').filter(line => line.trim() !== '');
        const header = lines.shift().split(',').map(h => h.trim());
        
        // Regex untuk menangani koma di dalam quotes
        const regex = /(?:"([^"]*)"|([^,]*))(?:,|$)/g;

        return lines.map(line => {
            const obj = {};
            let match;
            let i = 0;
            // Loop melalui setiap match di baris
            while (match = regex.exec(line)) {
                if (i >= header.length) break;
                
                // Ambil nilai dari grup yang cocok (grup 1 untuk quoted, grup 2 untuk unquoted)
                let value = match[1] !== undefined ? match[1] : match[2];
                value = value ? value.trim() : '';
                
                const key = header[i];

                // Mengubah angka menjadi tipe number
                if (!isNaN(value) && value.trim() !== '') {
                    obj[key] = Number(value);
                } else {
                    obj[key] = value;
                }
                i++;
            }
            return obj;
        });
    }


    // ===================================================================================
    // KONFIGURASI
    // ===================================================================================
    const CONFIG = {
        DELAY_BETWEEN_TESTS: 500,
        FORM_ACTION_URL: '/', 
        RESULT_CONTAINER_SELECTOR: '.persona-match',
    };
    // ===================================================================================

    // --- Helper Functions ---
    function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }
    function downloadCSV(data) { /* ... fungsi download tetap sama ... */
        if (!data || data.length === 0) { console.error("No data to download."); return; }
        const headers = Object.keys(data[0]);
        const rows = data.map(obj => headers.map(header => {
            let field = obj[header];
            if (typeof field === 'string' && field.includes(',')) return `"${field}"`;
            return field;
        }));
        const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement("a");
        const url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", "test_results.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        console.log('%c File CSV "test_results.csv" downloaded!', 'background: #28a745; color: #ffffff; font-size: 14px;');
    }
    
    async function runTestWithFetch(testCase) {
        console.log(`--- Testing: ${testCase.persona} - ${testCase.test_case_type} ---`);
        const formData = new FormData();
        formData.append('type', testCase.type.charAt(0).toUpperCase() + testCase.type.slice(1));
        formData.append('city', 'Depok Kota');
        formData.append('land_area', testCase.land_area);
        formData.append('building_area', testCase.building_area);
        formData.append('bedrooms', testCase.bedrooms);
        formData.append('bathrooms', testCase.bathrooms);
        formData.append('floors', testCase.floors);
        if (testCase.SCHOOL === 1) formData.append('SCHOOL', '1');
        if (testCase.HOSPITAL === 1) formData.append('HOSPITAL', '1');
        if (testCase.TRANSPORT === 1) formData.append('TRANSPORT', '1');
        if (testCase.MARKET === 1) formData.append('MARKET', '1');
        if (testCase.MALL === 1) formData.append('MALL', '1');
        const activeFacilities = testCase.facilities.split(', ').map(f => f.trim());
        activeFacilities.forEach(facility => { if (facility) { formData.append('facilities', facility); } });
        const response = await fetch(CONFIG.FORM_ACTION_URL, { method: 'POST', body: formData });
        if (!response.ok) throw new Error(`Server response: ${response.status}`);
        const resultHTML = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(resultHTML, "text/html");
        const resultContainer = doc.querySelector(CONFIG.RESULT_CONTAINER_SELECTOR);
        if (!resultContainer) return { ...testCase, found_persona: 'ERROR: Result container not found', found_score: 'ERROR' };
        const resultText = resultContainer.innerText;
        const personaMatch = resultText.match(/Best Persona Match:\s*(.*?)\s*\(/);
        const scoreMatch = resultText.match(/\((.*?)\/5\)/);
        const foundPersona = personaMatch ? personaMatch[1].trim() : 'Not Found';
        const foundScore = scoreMatch ? scoreMatch[1].trim() : 'Not Found';
        console.log(`Result -> Persona: ${foundPersona}, Score: ${foundScore}`);
        return { ...testCase, found_persona: foundPersona, found_score: foundScore };
    }

    // --- Main Execution Logic ---
    async function runAutomation() {
        if (testCases.length === 0) {
            statusArea.textContent = "Please load a CSV file first.";
            return;
        }

        const results = [];
        startBtn.disabled = true;
        fileInput.disabled = true;
        console.log(`%c Starting automation for ${testCases.length} cases...`, 'background: #222; color: #bada55; font-size: 16px;');

        for (let i = 0; i < testCases.length; i++) {
            statusArea.textContent = `Running test ${i + 1} of ${testCases.length}...`;
            try {
                const result = await runTestWithFetch(testCases[i]);
                results.push(result);
            } catch (error) {
                console.error(`Error during test case ${i + 1}:`, error);
                results.push({ ...testCases[i], found_persona: `FETCH_ERROR: ${error.message}`, found_score: 'ERROR' });
            }
            await sleep(CONFIG.DELAY_BETWEEN_TESTS);
        }

        console.log('%c --- TESTING COMPLETE --- ', 'background: #222; color: #bada55; font-size: 16px;');
        console.table(results);
        downloadCSV(results);
        statusArea.textContent = `Testing complete! Results downloaded.`;
        startBtn.disabled = false;
        fileInput.disabled = false;
    }
})();
