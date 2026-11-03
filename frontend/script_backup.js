/**
 * VibeCheck-AI Frontend Logic
 * Replaces all mock data with real backend endpoints:
 * - POST /api/analyze (Video upload & temporal localization)
 * - POST /api/analyze/text (Hinglish text risk detection)
 * - POST /api/policy/adapt (Experiment 2: Policy adaptation without ML retraining)
 * - GET  /api/history (SQLite activity log)
 * - GET  /api/history/{id} (Past analysis reload)
 */

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();

    // API Base URL (relative or fallback to backend port 8000)
    const API_BASE = window.location.origin.includes('5500')
        ? 'http://127.0.0.1:8000/api'
        : '/api';

    // State
    let currentInputType = 'video';
    let selectedVideoFile = null;
    let lastAnalysisResult = null;

    // DOM Elements
    const navButtons = document.querySelectorAll('.nav-btn');
    const viewSections = document.querySelectorAll('.view-section');
    const tabVideo = document.getElementById('tab-video');
    const tabText = document.getElementById('tab-text');
    const inputVideo = document.getElementById('input-video');
    const inputText = document.getElementById('input-text');
    const analyzeBtn = document.getElementById('analyze-btn');
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    const filePreviewInfo = document.getElementById('file-preview-info');
    const fileNameDisplay = document.getElementById('file-name-display');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const textInput = document.getElementById('text-input');
    const charCount = document.getElementById('char-count');
    const policyProfileSelect = document.getElementById('policy-profile-select');

    // Output Elements
    const outputPlaceholder = document.getElementById('output-placeholder');
    const outputResult = document.getElementById('output-result');
    const outputStatus = document.getElementById('output-status');
    const videoPlayer = document.getElementById('video-player');
    const textModeBanner = document.getElementById('text-mode-banner');
    const timelineContainer = document.getElementById('timeline');
    const timelineDurationLabel = document.getElementById('timeline-duration-label');
    const tickMid = document.getElementById('tick-mid');
    const tickEnd = document.getElementById('tick-end');
    const segmentsList = document.getElementById('segments-list');
    const segmentCountBadge = document.getElementById('segment-count-badge');
    const fullTranscriptView = document.getElementById('full-transcript-view');
    const adaptationBtn = document.getElementById('adaptation-btn');

    // Modal
    const adaptationModal = document.getElementById('adaptation-modal');
    const adaptationModalBody = document.getElementById('adaptation-modal-body');
    const closeAdaptationModal = document.getElementById('close-adaptation-modal');
    const closeAdaptationModalBtn = document.getElementById('close-adaptation-modal-btn');

    // User Dropdown
    const userMenuBtn = document.getElementById('user-menu-btn');
    const userDropdown = document.getElementById('user-dropdown');

    // --- 0. Dropdown & Navigation ---
    userMenuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        userDropdown.classList.toggle('hidden');
    });

    document.addEventListener('click', () => {
        if (!userDropdown.classList.contains('hidden')) {
            userDropdown.classList.add('hidden');
        }
    });

    window.switchTab = function (tabId) {
        navButtons.forEach(btn => btn.classList.remove('active'));
        const navEl = document.getElementById(`nav-${tabId}`);
        if (navEl) navEl.classList.add('active');

        viewSections.forEach(section => section.classList.add('hidden'));
        const targetView = document.getElementById(`view-${tabId}`);
        if (targetView) targetView.classList.remove('hidden');

        if (tabId === 'history') {
            loadHistoryData();
        }
        userDropdown.classList.add('hidden');
    };

    // --- 1. Input Type Switching ---
    window.switchInputType = function (type) {
        currentInputType = type;
        tabVideo.classList.remove('active');
        tabText.classList.remove('active');

        if (type === 'video') {
            tabVideo.classList.add('active');
            inputVideo.classList.remove('hidden');
            inputVideo.classList.add('flex');
            inputText.classList.add('hidden');
            inputText.classList.remove('flex');
        } else {
            tabText.classList.add('active');
            inputVideo.classList.add('hidden');
            inputVideo.classList.remove('flex');
            inputText.classList.remove('hidden');
            inputText.classList.add('flex');
        }
        validateInput();
    };

    function validateInput() {
        if (currentInputType === 'video') {
            const hasFile = selectedVideoFile !== null;
            analyzeBtn.disabled = !hasFile;
            if (hasFile) {
                analyzeBtn.innerHTML = `<i data-lucide="check-circle" class="w-5 h-5 mr-2"></i> Ready: ${selectedVideoFile.name}`;
            } else {
                analyzeBtn.innerHTML = `<i data-lucide="sparkles" class="w-5 h-5 mr-2"></i> Analyze Video`;
            }
        } else {
            const len = textInput.value.trim().length;
            analyzeBtn.disabled = len === 0;
            analyzeBtn.innerHTML = `<i data-lucide="sparkles" class="w-5 h-5 mr-2"></i> Analyze Text`;
        }
        lucide.createIcons();
    }

    // --- 2. File Upload Handling ---
    dropZone.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleSelectedFile(fileInput.files[0]);
        }
    });

    function handleSelectedFile(file) {
        selectedVideoFile = file;
        fileNameDisplay.textContent = `${file.name} (${(file.size / (1024 * 1024)).toFixed(1)} MB)`;
        filePreviewInfo.classList.remove('hidden');

        // Setup HTML5 video preview
        const fileUrl = URL.createObjectURL(file);
        videoPlayer.src = fileUrl;
        videoPlayer.classList.remove('hidden');
        textModeBanner.classList.add('hidden');

        validateInput();
    }

    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        selectedVideoFile = null;
        fileInput.value = '';
        filePreviewInfo.classList.add('hidden');
        videoPlayer.src = '';
        videoPlayer.classList.add('hidden');
        validateInput();
    });

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
            handleSelectedFile(e.dataTransfer.files[0]);
        }
    });

    // --- 3. Text Input & Quick Samples ---
    textInput.addEventListener('input', () => {
        const len = textInput.value.length;
        charCount.textContent = `${len} / 2000`;
        if (len > 2000) {
            charCount.classList.add('text-rose-500', 'font-bold');
        } else {
            charCount.classList.remove('text-rose-500', 'font-bold');
        }
        validateInput();
    });

    document.querySelectorAll('.quick-sample-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            textInput.value = btn.getAttribute('data-sample');
            textInput.dispatchEvent(new Event('input'));
        });
    });

    // --- 4. Real Analysis Execution ---
    analyzeBtn.addEventListener('click', async () => {
        analyzeBtn.disabled = true;
        const originalText = analyzeBtn.innerHTML;
        analyzeBtn.innerHTML = `<i data-lucide="loader-2" class="w-5 h-5 mr-2 animate-spin"></i> Processing Pipeline...`;
        lucide.createIcons();

        outputStatus.textContent = 'Transcribing & Evaluating...';
        outputStatus.className = 'text-xs font-bold text-indigo-700 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-200 animate-pulse';

        const selectedPolicyVersion = policyProfileSelect.value; // 'v1' or 'v2'

        try {
            let data;
            if (currentInputType === 'video') {
                if (!selectedVideoFile) return;

                const formData = new FormData();
                formData.append('file', selectedVideoFile);

                const res = await fetch(`${API_BASE}/analyze?youtube_version=${selectedPolicyVersion}&meta_version=${selectedPolicyVersion}`, {
                    method: 'POST',
                    body: formData,
                });

                if (!res.ok) {
                    const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
                    throw new Error(err.detail || `Server returned ${res.status}`);
                }
                data = await res.json();
            } else {
                const textVal = textInput.value.trim();
                const res = await fetch(`${API_BASE}/analyze/text`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text: textVal,
                        youtube_policy_version: selectedPolicyVersion,
                        meta_policy_version: selectedPolicyVersion,
                    }),
                });

                if (!res.ok) {
                    const err = await res.json().catch(() => ({ detail: 'Text analysis failed' }));
                    throw new Error(err.detail || `Server returned ${res.status}`);
                }
                data = await res.json();
            }

            lastAnalysisResult = data;
            renderAnalysisDashboard(data);

            outputStatus.textContent = 'Completed';
            outputStatus.className = 'text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200';

        } catch (error) {
            console.error('Analysis error:', error);
            alert(`Analysis Error: ${error.message}`);
            outputStatus.textContent = 'Failed';
            outputStatus.className = 'text-xs font-bold text-rose-700 bg-rose-50 px-3 py-1 rounded-full border border-rose-200';
        } finally {
            analyzeBtn.innerHTML = originalText;
            validateInput();
            lucide.createIcons();
        }
    });

    // Helper: format seconds to MM:SS
    function formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    // Helper: format decimal seconds
    function formatTimeSec(seconds) {
        return `${seconds.toFixed(1)}s`;
    }

    // --- 5. Render Real Dashboard Output ---
    function renderAnalysisDashboard(data) {
        outputPlaceholder.classList.add('hidden');
        outputResult.classList.remove('hidden');
        adaptationBtn.classList.remove('hidden');

        const totalDuration = Math.max(1.0, data.duration_seconds || 1.0);
        timelineDurationLabel.textContent = formatTime(totalDuration);
        tickMid.textContent = formatTime(totalDuration / 2);
        tickEnd.textContent = formatTime(totalDuration);

        // Player Mode
        if (currentInputType === 'video' && selectedVideoFile) {
            videoPlayer.classList.remove('hidden');
            textModeBanner.classList.add('hidden');
        } else {
            videoPlayer.classList.add('hidden');
            textModeBanner.classList.remove('hidden');
            document.getElementById('detected-lang-badge').textContent = data.language || 'code-mixed';
        }

        // Render Platform Summary Cards
        const ytOverview = data.policy_overview?.youtube || {};
        const metaOverview = data.policy_overview?.instagram_meta || {};

        const ytSummaryBadge = document.getElementById('yt-summary-badge');
        ytSummaryBadge.textContent = `${ytOverview.potential_violations || 0} Violations, ${ytOverview.requires_review || 0} Review`;
        ytSummaryBadge.className = ytOverview.potential_violations > 0
            ? 'text-[10px] font-bold px-2 py-0.5 rounded bg-rose-100 text-rose-800'
            : (ytOverview.requires_review > 0
                ? 'text-[10px] font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-800'
                : 'text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800');

        document.getElementById('yt-summary-text').textContent =
            `Highest Severity: ${ytOverview.highest_severity || 'Low'} • Community Guidelines`;

        const metaSummaryBadge = document.getElementById('meta-summary-badge');
        metaSummaryBadge.textContent = `${metaOverview.potential_violations || 0} Violations, ${metaOverview.requires_review || 0} Review`;
        metaSummaryBadge.className = metaOverview.potential_violations > 0
            ? 'text-[10px] font-bold px-2 py-0.5 rounded bg-rose-100 text-rose-800'
            : (metaOverview.requires_review > 0
                ? 'text-[10px] font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-800'
                : 'text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800');

        document.getElementById('meta-summary-text').textContent =
            `Highest Severity: ${metaOverview.highest_severity || 'Low'} • Community Standards`;

        // Render Timeline
        timelineContainer.innerHTML = '';
        const segments = data.segments || [];

        segments.forEach((seg, idx) => {
            const startPct = Math.max(0, Math.min(100, (seg.start / totalDuration) * 100));
            const widthPct = Math.max(1, Math.min(100 - startPct, ((seg.end - seg.start) / totalDuration) * 100));

            const segEl = document.createElement('div');
            let colorClass = 'safe';
            if (seg.label === 'hate_speech') colorClass = 'harmful';
            else if (seg.label === 'harassment') colorClass = 'offensive';

            segEl.className = `timeline-segment ${colorClass}`;
            segEl.style.left = `${startPct}%`;
            segEl.style.width = `${widthPct}%`;
            segEl.title = `[${formatTime(seg.start)} - ${formatTime(seg.end)}] (${seg.label}, ${(seg.confidence * 100).toFixed(0)}%)\n"${seg.text}"`;

            segEl.addEventListener('click', () => {
                seekVideoTo(seg.start);
            });

            timelineContainer.appendChild(segEl);
        });

        // Render Segments List with Dual Policy Assessments
        segmentsList.innerHTML = '';
        segmentCountBadge.textContent = `${segments.length} segment(s)`;

        if (segments.length === 0) {
            segmentsList.innerHTML = `
                <div class="p-4 bg-white rounded-xl border border-slate-200 text-center text-xs text-slate-500">
                    No speech detected in this video.
                </div>
            `;
        }

        segments.forEach((seg, idx) => {
            const card = document.createElement('div');
            const isRisk = seg.label !== 'normal';

            const borderClass = seg.label === 'hate_speech'
                ? 'border-l-4 border-l-rose-500 border-rose-100 bg-white'
                : (seg.label === 'harassment'
                    ? 'border-l-4 border-l-amber-500 border-amber-100 bg-white'
                    : 'border-l-4 border-l-emerald-500 border-slate-100 bg-white');

            const labelBadgeColor = seg.label === 'hate_speech'
                ? 'bg-rose-50 text-rose-700 border-rose-200'
                : (seg.label === 'harassment'
                    ? 'bg-amber-50 text-amber-700 border-amber-200'
                    : 'bg-emerald-50 text-emerald-700 border-emerald-200');

            const yt = seg.youtube_policy || {};
            const ig = seg.instagram_policy || {};

            card.className = `p-4 rounded-xl border shadow-sm space-y-3 ${borderClass}`;
            card.innerHTML = `
                <div class="flex justify-between items-center">
                    <button type="button" class="seek-btn flex items-center space-x-1.5 text-xs font-bold font-mono text-indigo-700 bg-indigo-50 hover:bg-indigo-100 px-2 py-1 rounded border border-indigo-200 transition-colors" data-time="${seg.start}">
                        <i data-lucide="play-circle" class="w-3.5 h-3.5"></i>
                        <span>${formatTime(seg.start)} - ${formatTime(seg.end)}</span>
                    </button>
                    <div class="flex items-center space-x-2">
                        <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${labelBadgeColor}">
                            ${seg.label.replace('_', ' ')}
                        </span>
                        <span class="text-[11px] font-bold text-slate-500 font-mono">
                            ${(seg.confidence * 100).toFixed(1)}% conf
                        </span>
                    </div>
                </div>

                <p class="text-xs font-semibold text-slate-800 leading-relaxed bg-slate-50/70 p-2.5 rounded-lg border border-slate-100">
                    "${escapeHtml(seg.text)}"
                </p>

                <!-- Dual Platform Policy Cards Side-by-Side -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                    <!-- YouTube Assessment -->
                    <div class="bg-red-50/40 p-3 rounded-xl border border-red-100 space-y-1.5">
                        <div class="flex justify-between items-center">
                            <span class="text-[11px] font-bold text-red-950 flex items-center">
                                <i data-lucide="video" class="w-3 h-3 mr-1 text-red-600"></i> YouTube Assessment
                            </span>
                            <span class="text-[9px] font-bold px-1.5 py-0.5 rounded ${getStatusBadgeClass(yt.status)}">
                                ${yt.status_label || 'Low Concern'}
                            </span>
                        </div>
                        <p class="text-[10px] text-slate-600">
                            <strong>Category:</strong> ${yt.policy_category || 'General'} (${yt.severity || 'Low'} Severity)
                        </p>
                        <p class="text-[10px] text-slate-600 leading-snug">
                            <strong>Assessment:</strong> ${yt.recommended_action || 'No intervention required.'}
                        </p>
                        ${yt.source_url ? `
                            <a href="${yt.source_url}" target="_blank" class="inline-flex items-center text-[9px] text-red-700 hover:underline pt-0.5">
                                <i data-lucide="external-link" class="w-2.5 h-2.5 mr-1"></i> ${yt.source_title || 'YouTube Policy Source'}
                            </a>
                        ` : ''}
                    </div>

                    <!-- Meta / Instagram Assessment -->
                    <div class="bg-pink-50/40 p-3 rounded-xl border border-pink-100 space-y-1.5">
                        <div class="flex justify-between items-center">
                            <span class="text-[11px] font-bold text-pink-950 flex items-center">
                                <i data-lucide="instagram" class="w-3 h-3 mr-1 text-pink-600"></i> Instagram/Meta Assessment
                            </span>
                            <span class="text-[9px] font-bold px-1.5 py-0.5 rounded ${getStatusBadgeClass(ig.status)}">
                                ${ig.status_label || 'Low Concern'}
                            </span>
                        </div>
                        <p class="text-[10px] text-slate-600">
                            <strong>Category:</strong> ${ig.policy_category || 'General'} (${ig.severity || 'Low'} Severity)
                        </p>
                        <p class="text-[10px] text-slate-600 leading-snug">
                            <strong>Assessment:</strong> ${ig.recommended_action || 'No intervention required.'}
                        </p>
                        ${ig.source_url ? `
                            <a href="${ig.source_url}" target="_blank" class="inline-flex items-center text-[9px] text-pink-700 hover:underline pt-0.5">
                                <i data-lucide="external-link" class="w-2.5 h-2.5 mr-1"></i> ${ig.source_title || 'Meta Standards Source'}
                            </a>
                        ` : ''}
                    </div>
                </div>
            `;

            card.querySelector('.seek-btn').addEventListener('click', () => {
                seekVideoTo(seg.start);
            });

            segmentsList.appendChild(card);
        });

        // Render Full Transcript View
        fullTranscriptView.innerHTML = '';
        segments.forEach((seg) => {
            const row = document.createElement('div');
            row.className = 'py-1 flex items-start space-x-2 cursor-pointer hover:bg-indigo-50/50 p-1 rounded transition-colors';
            const riskColor = seg.label === 'hate_speech' ? 'text-rose-600 font-bold' : (seg.label === 'harassment' ? 'text-amber-600 font-bold' : 'text-slate-700');
            row.innerHTML = `
                <span class="font-mono text-[10px] text-indigo-600 font-semibold flex-shrink-0 seek-link">[${formatTime(seg.start)}]</span>
                <span class="${riskColor} text-xs flex-1">${escapeHtml(seg.text)}</span>
            `;
            row.addEventListener('click', () => seekVideoTo(seg.start));
            fullTranscriptView.appendChild(row);
        });

        lucide.createIcons();
    }

    function seekVideoTo(seconds) {
        if (videoPlayer && !videoPlayer.classList.contains('hidden')) {
            videoPlayer.currentTime = seconds;
            videoPlayer.play().catch(() => {});
            videoPlayer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    function getStatusBadgeClass(status) {
        if (status === 'potential_policy_violation') {
            return 'bg-rose-100 text-rose-800 border border-rose-200';
        } else if (status === 'requires_review') {
            return 'bg-amber-100 text-amber-800 border border-amber-200';
        } else {
            return 'bg-emerald-100 text-emerald-800 border border-emerald-200';
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // --- 6. Policy Adaptation Experiment 2 Modal ---
    adaptationBtn.addEventListener('click', async () => {
        if (!lastAnalysisResult || !lastAnalysisResult.segments) return;

        adaptationModal.classList.remove('hidden');
        adaptationModalBody.innerHTML = `
            <div class="p-8 text-center text-slate-500">
                <i data-lucide="loader-2" class="w-6 h-6 animate-spin mx-auto mb-2 text-indigo-600"></i>
                Simulating policy transition across v1.2 Standard vs. v2.0 Strict profiles...
            </div>
        `;
        lucide.createIcons();

        try {
            const res = await fetch(`${API_BASE}/policy/adapt`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    events: lastAnalysisResult.segments,
                    v1_version: 'v1',
                    v2_version: 'v2',
                }),
            });

            if (!res.ok) throw new Error('Policy adaptation simulation failed');
            const adaptData = await res.json();
            renderAdaptationModal(adaptData);

        } catch (err) {
            adaptationModalBody.innerHTML = `
                <div class="p-4 bg-rose-50 text-rose-700 rounded-xl">
                    Failed to run experiment: ${err.message}
                </div>
            `;
        }
    });

    function renderAdaptationModal(adaptData) {
        const v1List = adaptData.policy_v1_results || [];
        const v2List = adaptData.policy_v2_results || [];

        let html = `
            <div class="p-3 bg-indigo-50 border border-indigo-100 rounded-xl text-indigo-900 leading-relaxed">
                <strong>Empirical Principle Demonstrated:</strong> ${adaptData.principle}<br>
                ${adaptData.experiment_note}
            </div>
            <div class="space-y-3 pt-2">
        `;

        v1List.forEach((ev1, idx) => {
            const ev2 = v2List[idx] || {};
            const yt1 = ev1.youtube || {};
            const yt2 = ev2.youtube || {};
            const ig1 = ev1.instagram_meta || {};
            const ig2 = ev2.instagram_meta || {};

            const ytChanged = yt1.status !== yt2.status;
            const igChanged = ig1.status !== ig2.status;

            html += `
                <div class="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
                    <div class="flex justify-between items-center text-slate-800">
                        <span class="font-mono font-bold text-indigo-600">[${formatTime(ev1.start)} - ${formatTime(ev1.end)}]</span>
                        <span class="font-bold text-xs">ML Event: <span class="uppercase text-slate-700">${ev1.label}</span> (${(ev1.confidence * 100).toFixed(1)}%)</span>
                    </div>
                    <p class="text-slate-700 italic">"${escapeHtml(ev1.text)}"</p>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                        <!-- YouTube Comparison -->
                        <div class="p-2.5 bg-white rounded-lg border ${ytChanged ? 'border-amber-300 ring-2 ring-amber-100' : 'border-slate-200'}">
                            <div class="font-bold text-[11px] text-slate-800 mb-1 flex justify-between">
                                <span>YouTube Policy Assessment</span>
                                ${ytChanged ? '<span class="text-[9px] bg-amber-100 text-amber-800 px-1.5 py-0.2 rounded font-bold">Policy Shifted</span>' : ''}
                            </div>
                            <div class="space-y-1 text-[10px]">
                                <div><span class="text-slate-400">v1.2 Standard:</span> <span class="font-bold ${getStatusBadgeClass(yt1.status)} px-1 rounded">${yt1.status_label}</span></div>
                                <div><span class="text-slate-400">v2.0 Strict:</span> <span class="font-bold ${getStatusBadgeClass(yt2.status)} px-1 rounded">${yt2.status_label}</span></div>
                            </div>
                        </div>

                        <!-- Meta Comparison -->
                        <div class="p-2.5 bg-white rounded-lg border ${igChanged ? 'border-amber-300 ring-2 ring-amber-100' : 'border-slate-200'}">
                            <div class="font-bold text-[11px] text-slate-800 mb-1 flex justify-between">
                                <span>Instagram/Meta Assessment</span>
                                ${igChanged ? '<span class="text-[9px] bg-amber-100 text-amber-800 px-1.5 py-0.2 rounded font-bold">Policy Shifted</span>' : ''}
                            </div>
                            <div class="space-y-1 text-[10px]">
                                <div><span class="text-slate-400">v2026.1 Standard:</span> <span class="font-bold ${getStatusBadgeClass(ig1.status)} px-1 rounded">${ig1.status_label}</span></div>
                                <div><span class="text-slate-400">v2026.2 Strict:</span> <span class="font-bold ${getStatusBadgeClass(ig2.status)} px-1 rounded">${ig2.status_label}</span></div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        html += `</div>`;
        adaptationModalBody.innerHTML = html;
        lucide.createIcons();
    }

    closeAdaptationModal.addEventListener('click', () => adaptationModal.classList.add('hidden'));
    closeAdaptationModalBtn.addEventListener('click', () => adaptationModal.classList.add('hidden'));

    // --- 7. History Activity Loader ---
    window.loadHistoryData = async function () {
        const historyTableBody = document.getElementById('history-table-body');
        if (!historyTableBody) return;

        historyTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-6 text-center text-slate-400 text-xs">
                    <i data-lucide="loader-2" class="w-4 h-4 animate-spin inline mr-1 text-indigo-600"></i> Loading activity logs...
                </td>
            </tr>
        `;
        lucide.createIcons();

        try {
            const res = await fetch(`${API_BASE}/history`);
            if (!res.ok) throw new Error('Failed to load history');
            const items = await res.json();

            if (items.length === 0) {
                historyTableBody.innerHTML = `
                    <tr>
                        <td colspan="6" class="px-6 py-8 text-center text-slate-400 text-xs">
                            No past analyses recorded yet. Run a video or text analysis above to log activity.
                        </td>
                    </tr>
                `;
                return;
            }

            historyTableBody.innerHTML = '';
            items.forEach((item) => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-50/80 transition-colors group';

                const dateStr = new Date(item.created_at).toLocaleString();
                const sevBadgeClass = item.highest_severity === 'Critical' || item.highest_severity === 'High'
                    ? 'bg-rose-50 text-rose-700 border-rose-100'
                    : (item.highest_severity === 'Medium-High' || item.highest_severity === 'Medium'
                        ? 'bg-amber-50 text-amber-700 border-amber-100'
                        : 'bg-emerald-50 text-emerald-700 border-emerald-100');

                tr.innerHTML = `
                    <td class="px-6 py-4 text-slate-500 font-mono text-xs">${dateStr}</td>
                    <td class="px-6 py-4 flex items-center space-x-2">
                        <div class="p-1.5 bg-blue-50 text-blue-600 rounded border border-blue-100"><i data-lucide="file" class="w-3.5 h-3.5"></i></div>
                        <span class="font-medium text-slate-700 text-xs">${escapeHtml(item.filename || item.id)}</span>
                    </td>
                    <td class="px-6 py-4 text-slate-500 text-xs font-mono">${item.duration_seconds.toFixed(1)}s</td>
                    <td class="px-6 py-4 text-xs font-semibold text-slate-700">${item.risk_count} event(s)</td>
                    <td class="px-6 py-4">
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold border ${sevBadgeClass}">
                            ${item.highest_severity}
                        </span>
                    </td>
                    <td class="px-6 py-4 text-right">
                        <button class="view-history-detail-btn text-indigo-600 font-semibold hover:text-indigo-800 text-xs group-hover:underline" data-id="${item.id}">
                            View Report
                        </button>
                    </td>
                `;

                tr.querySelector('.view-history-detail-btn').addEventListener('click', async () => {
                    await loadHistoryDetail(item.id);
                });

                historyTableBody.appendChild(tr);
            });

            lucide.createIcons();

        } catch (err) {
            historyTableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="px-6 py-6 text-center text-rose-500 text-xs">
                        Failed to fetch activity history: ${err.message}
                    </td>
                </tr>
            `;
        }
    };

    async function loadHistoryDetail(id) {
        try {
            const res = await fetch(`${API_BASE}/history/${id}`);
            if (!res.ok) throw new Error('Analysis not found');
            const data = await res.json();
            lastAnalysisResult = data;
            switchTab('new-analysis');
            renderAnalysisDashboard(data);
        } catch (err) {
            alert(`Could not load report: ${err.message}`);
        }
    }

    // Initial check
    validateInput();
});