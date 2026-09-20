document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    lucide.createIcons();

    // --- DOM Elements ---
    const navButtons = document.querySelectorAll('.nav-btn');
    const viewSections = document.querySelectorAll('.view-section');
    const tabVideo = document.getElementById('tab-video');
    const tabText = document.getElementById('tab-text');
    const inputVideo = document.getElementById('input-video');
    const inputText = document.getElementById('input-text');
    const analyzeBtn = document.getElementById('analyze-btn');
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    const textInput = document.getElementById('text-input');
    const charCount = document.getElementById('char-count');
    
    // Output elements
    const outputPlaceholder = document.getElementById('output-placeholder');
    const outputResult = document.getElementById('output-result');
    const outputStatus = document.getElementById('output-status');

    // User Dropdown
    const userMenuBtn = document.getElementById('user-menu-btn');
    const userDropdown = document.getElementById('user-dropdown');

    let currentInputType = 'video'; // 'video' or 'text'

    // --- 0. User Dropdown Toggle ---
    userMenuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        userDropdown.classList.toggle('hidden');
    });

    document.addEventListener('click', () => {
        if (!userDropdown.classList.contains('hidden')) {
            userDropdown.classList.add('hidden');
        }
    });

    // --- 1. Sidebar Navigation (SPA Routing) ---
    window.switchTab = function(tabId) {
        // Update active state on sidebar
        navButtons.forEach(btn => btn.classList.remove('active'));
        document.getElementById(`nav-${tabId}`).classList.add('active');

        // Show/hide views with a slight fade effect
        viewSections.forEach(section => {
            section.classList.add('hidden');
            section.style.opacity = '0';
        });
        
        const activeView = document.getElementById(`view-${tabId}`);
        activeView.classList.remove('hidden');
        // Trigger reflow to enable transition
        void activeView.offsetWidth;
        activeView.style.opacity = '1';
        activeView.style.transition = 'opacity 0.3s ease';
        
        // Close dropdown if open
        userDropdown.classList.add('hidden');
    };

    // --- 2. Input Type Toggling (Video vs Text) ---
    window.switchInputType = function(type) {
        currentInputType = type;
        
        // Reset tab styles
        tabVideo.classList.remove('active');
        tabText.classList.remove('active');
        
        if (type === 'video') {
            tabVideo.classList.add('active');
            inputVideo.classList.remove('hidden');
            inputVideo.classList.add('flex');
            inputText.classList.add('hidden');
            inputText.classList.remove('flex');
            validateInput();
        } else {
            tabText.classList.add('active');
            inputVideo.classList.add('hidden');
            inputVideo.classList.remove('flex');
            inputText.classList.remove('hidden');
            inputText.classList.add('flex');
            validateInput();
        }
    };

    // --- 3. Input Validation & Button State ---
    function validateInput() {
        if (currentInputType === 'video') {
            analyzeBtn.disabled = fileInput.files.length === 0;
            if(fileInput.files.length > 0) {
                analyzeBtn.innerHTML = `<i data-lucide="check-circle" class="w-5 h-5 mr-2"></i> Ready: ${fileInput.files[0].name}`;
            } else {
                analyzeBtn.innerHTML = `<i data-lucide="sparkles" class="w-5 h-5 mr-2"></i> Analyze Content`;
            }
        } else {
            const textLength = textInput.value.trim().length;
            analyzeBtn.disabled = textLength === 0;
            analyzeBtn.innerHTML = `<i data-lucide="sparkles" class="w-5 h-5 mr-2"></i> Analyze Text`;
        }
        // Re-initialize icons since innerHTML changed
        lucide.createIcons();
    }

    // --- 4. File Upload Handling ---
    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', () => {
        validateInput();
    });

    // Drag and Drop visual feedback
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-indigo-500', 'bg-indigo-50/50');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('border-indigo-500', 'bg-indigo-50/50');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-indigo-500', 'bg-indigo-50/50');
        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            validateInput();
        }
    });

    // --- 5. Text Input Handling ---
    textInput.addEventListener('input', () => {
        const len = textInput.value.length;
        charCount.textContent = `${len} / 2000 chars`;
        if (len > 2000) {
            charCount.classList.add('text-rose-500', 'font-bold');
        } else {
            charCount.classList.remove('text-rose-500', 'font-bold');
        }
        validateInput();
    });

    // --- 6. Mock Analysis Execution ---
    analyzeBtn.addEventListener('click', () => {
        const originalText = analyzeBtn.innerHTML;
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = `<i data-lucide="loader-2" class="w-5 h-5 mr-2 animate-spin"></i> Processing...`;
        lucide.createIcons();
        analyzeBtn.classList.add('opacity-80');
        outputStatus.textContent = 'Processing...';
        outputStatus.className = 'text-xs font-bold text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full';

        // Simulate API delay (e.g., Whisper + HateBERT processing)
        setTimeout(() => {
            // Hide placeholder, show result
            outputPlaceholder.classList.add('hidden');
            outputResult.classList.remove('hidden');
            outputResult.classList.add('flex');
            
            outputStatus.textContent = 'Completed';
            outputStatus.className = 'text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200';
            
            // Reset button state
            analyzeBtn.innerHTML = originalText;
            lucide.createIcons();
            analyzeBtn.classList.remove('opacity-80');
            validateInput();
            
        }, 2000);
    });

    // Initialize validation state on load
    validateInput();
});