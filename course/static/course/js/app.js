/* ===== main.js ===== */
/**
 * MICROPROCESSOR SYSTEMS — Main JavaScript
 * Handles UI interactions, sidebar toggling, mobile menu, and global functionality.
 */

(function () {
    'use strict';

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function () {
        initTooltips();
        initSidebar();
        initAutoDismissAlerts();
        initSmoothScroll();
        initMobileNavbar();
        initTouchFeedback();
    });

    /**
     * Initialize Bootstrap tooltips
     */
    function initTooltips() {
        var tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]')
        );
        tooltipTriggerList.forEach(function (el) {
            new bootstrap.Tooltip(el);
        });
    }

    /**
     * Create sidebar backdrop element once
     */
    function createBackdrop() {
        var existing = document.querySelector('.sidebar-backdrop');
        if (existing) return existing;
        var backdrop = document.createElement('div');
        backdrop.className = 'sidebar-backdrop';
        backdrop.addEventListener('click', function () {
            var sidebar = document.getElementById('sidebarNav');
            if (sidebar && sidebar.classList.contains('show')) {
                sidebar.classList.remove('show');
                backdrop.classList.remove('show');
            }
        });
        document.body.appendChild(backdrop);
        return backdrop;
    }

    /**
     * Initialize sidebar behavior on mobile
     */
    function initSidebar() {
        var sidebar = document.getElementById('sidebarNav');
        if (!sidebar) return;

        var backdrop = createBackdrop();

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function (e) {
            var isMobile = window.innerWidth < 992;
            if (!isMobile) return;

            var isClickInside = sidebar.contains(e.target);
            var isToggle = e.target.closest('[onclick="toggleSidebar()"]') ||
                           e.target.closest('.sidebar-close') ||
                           e.target.closest('#sidebarToggleBtn');

            if (!isClickInside && !isToggle && sidebar.classList.contains('show')) {
                sidebar.classList.remove('show');
                backdrop.classList.remove('show');
            }
        });

        // Handle window resize
        var resizeTimer;
        window.addEventListener('resize', function () {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function () {
                if (window.innerWidth >= 992) {
                    sidebar.classList.remove('show');
                    backdrop.classList.remove('show');
                    sidebar.style.transform = '';
                }
            }, 250);
        });

        // Expose backdrop for toggleSidebar
        window.__sidebarBackdrop = backdrop;
    }

    /**
     * Auto-dismiss flash alerts after 5 seconds
     */
    function initAutoDismissAlerts() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function (alert) {
            setTimeout(function () {
                var bsAlert = bootstrap.Alert.getInstance(alert);
                if (bsAlert) {
                    bsAlert.close();
                } else {
                    // Fallback manual close
                    alert.style.transition = 'opacity 0.5s ease';
                    alert.style.opacity = '0';
                    setTimeout(function () {
                        alert.remove();
                    }, 500);
                }
            }, 5000);
        });
    }

    /**
     * Smooth scroll for anchor links
     */
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
            anchor.addEventListener('click', function (e) {
                var target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start',
                    });
                }
            });
        });
    }

    /**
     * Global toggle sidebar function (used by inline onclick)
     */
    window.toggleSidebar = function () {
        var sidebar = document.getElementById('sidebarNav');
        var content = document.getElementById('learningContent');
        if (!sidebar) return;

        var isMobile = window.innerWidth < 992;

        if (isMobile) {
            sidebar.classList.toggle('show');
            var backdrop = window.__sidebarBackdrop;
            if (backdrop) {
                backdrop.classList.toggle('show');
            }
        } else {
            sidebar.classList.toggle('collapsed');
            if (content) {
                content.classList.toggle('expanded');
            }

            var icon = document.getElementById('sidebarCollapseIcon');
            if (icon) {
                if (sidebar.classList.contains('collapsed')) {
                    icon.className = 'bi bi-chevron-right';
                } else {
                    icon.className = 'bi bi-chevron-left';
                }
            }
        }
    };

    /**
     * Mobile navbar: auto-close menu after clicking a link
     */
    function initMobileNavbar() {
        var navbarToggler = document.querySelector('.navbar-toggler');
        var navbarCollapse = document.getElementById('navbarMain');

        if (!navbarToggler || !navbarCollapse) return;

        // Close navbar on link click on mobile
        navbarCollapse.addEventListener('click', function (e) {
            var link = e.target.closest('.nav-link');
            if (link && window.innerWidth < 992) {
                var bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                if (bsCollapse) {
                    bsCollapse.hide();
                }
            }
        });
    }

    /**
     * Touch feedback: prevent double-tap zoom on interactive buttons
     */
    function initTouchFeedback() {
        // Add touch feedback for simulator buttons
        document.querySelectorAll('.simulator-buttons .btn, .num-quick-btn, .btn-accent, .btn-outline-accent')
            .forEach(function (btn) {
                btn.addEventListener('touchstart', function () {
                    // Small visual feedback that doesn't interfere with click
                    this.style.opacity = '0.85';
                }, { passive: true });
                btn.addEventListener('touchend', function () {
                    this.style.opacity = '';
                }, { passive: true });
            });

        // Prevent 300ms delay on touch devices for interactive elements
        document.addEventListener('touchstart', function () {}, { passive: true });
    }

    /**
     * Utility: detect if touch device
     */
    window.isTouchDevice = function () {
        return ('ontouchstart' in window) ||
               (navigator.maxTouchPoints > 0) ||
               (navigator.msMaxTouchPoints > 0);
    };

    console.log('Main.js loaded — Microprocessor Systems Course [Mobile Ready]');

})();


/* ===== pipeline.js ===== */
/**
 * MICROPROCESSOR SYSTEMS — Pipeline Visualization Simulator
 *
 * Implements a 5-stage RISC pipeline visualizer:
 *   IF (Instruction Fetch)
 *   ID (Instruction Decode)
 *   EX (Execute)
 *   MEM (Memory Access)
 *   WB (Write Back)
 *
 * Color legend:
 *   Green (#d4edda) – Active stage (normal flow)
 *   Red (#f8d7da)   – Stall / hazard
 *   Blue (#cce5ff)  – Write-back completed
 */

(function () {
    'use strict';

    // ---- State Variables ----
    var instructions = [];
    var pipelineState = [];   // Array of arrays: [instr_idx, stage, cycle]
    var currentCycle = 0;
    var maxCycles = 20;
    var isRunning = false;
    var isPaused = false;
    var timerId = null;
    var simSpeed = 800; // ms per cycle

    // Stage names and display labels
    var STAGES = ['IF', 'ID', 'EX', 'MEM', 'WB'];
    var STAGE_COLORS = {
        'IF':  'pipeline-active',
        'ID':  'pipeline-active',
        'EX':  'pipeline-active',
        'MEM': 'pipeline-active',
        'WB':  'pipeline-wb',
    };

    // Register file
    var registers = {};
    for (var i = 0; i < 16; i++) {
        registers['R' + i] = 0;
    }

    // ---- Initialization ----
    function init() {
        // Find the pipeline simulator container
        var container = document.querySelector('.pipeline-simulator');
        if (!container) return;

        console.log('Pipeline Simulator initialized');

        // Initialize register display
        updateRegisterDisplay();
    }

    // ---- Core Pipeline Simulation ----
    function parseInstructions(text) {
        var lines = text.split('\n');
        var parsed = [];
        lines.forEach(function (line) {
            line = line.trim();
            if (line && !line.startsWith(';') && !line.startsWith('#')) {
                parsed.push(line);
            }
        });
        return parsed;
    }

    function buildPipeline(instructions) {
        var numInstr = instructions.length;
        var numCycles = numInstr + 5; // 5 pipeline stages
        if (numCycles > maxCycles) maxCycles = numCycles;

        pipelineState = [];

        for (var i = 0; i < numInstr; i++) {
            var stages = [];
            for (var s = 0; s < STAGES.length; s++) {
                var cycle = i + s + 1; // First instr starts at cycle 1
                if (cycle <= numCycles) {
                    // Check for simple data hazard detection
                    var hazard = detectHazard(instructions, i, s, cycle);
                    stages.push({
                        instrIdx: i,
                        stage: STAGES[s],
                        cycle: cycle,
                        hazard: hazard,
                        completed: cycle < numCycles,
                    });
                }
            }
            pipelineState.push(stages);
        }

        return pipelineState;
    }

    function detectHazard(instructions, instrIdx, stageIdx, cycle) {
        // Simple hazard detection:
        // If EX stage and previous instruction writes to register
        // that this instruction reads, flag a stall
        if (stageIdx === 2) { // EX stage
            var currentInstr = instructions[instrIdx] || '';
            // Check if previous instruction (if any) is in MEM or WB
            if (instrIdx > 0) {
                var prevInstr = instructions[instrIdx - 1] || '';
                var currRegs = extractRegisters(currentInstr);
                var prevRegs = extractRegisters(prevInstr);
                // Simple hazard: if destination register of prev is source of curr
                if (prevRegs.dest && currRegs.src1 && prevRegs.dest === currRegs.src1) {
                    return true; // data hazard
                }
                if (prevRegs.dest && currRegs.src2 && prevRegs.dest === currRegs.src2) {
                    return true;
                }
            }
        }
        return false;
    }

    function extractRegisters(instr) {
        // Very simple register extractor for basic RISC instructions
        var result = { dest: null, src1: null, src2: null };
        // Pattern: OP RD, RS1, RS2  or  OP RD, RS1  or  OP RD, OFFSET(RS1)
        var parts = instr.replace(/,/g, ' ').split(/\s+/);
        if (parts.length >= 2) {
            result.dest = parts[1] && parts[1].toUpperCase();
            if (parts.length >= 3) {
                result.src1 = parts[2] && parts[2].toUpperCase();
                // Remove parentheses
                if (result.src1 && result.src1.includes('(')) {
                    var match = result.src1.match(/\(?(R\d+)/);
                    result.src1 = match ? match[1] : result.src1;
                }
            }
            if (parts.length >= 4) {
                result.src2 = parts[3] && parts[3].toUpperCase();
                if (result.src2 && result.src2.includes(')')) {
                    result.src2 = result.src2.replace(')', '');
                }
            }
        }
        return result;
    }

    function renderPipeline() {
        var tableBody = document.getElementById('pipelineBody');
        if (!tableBody) return;

        // Build the table
        var html = '';
        for (var i = 0; i < pipelineState.length; i++) {
            var stages = pipelineState[i];
            var instrText = instructions[i] || '???';
            var maxWidth = maxCycles;

            html += '<tr>';
            html += '<td class="text-start fw-semibold"><small>' + instrText + '</small></td>';

            // Build cycle-by-cycle display
            var cycleMap = {};
            stages.forEach(function (s) {
                if (s.cycle <= maxCycles) {
                    cycleMap[s.cycle] = s;
                }
            });

            for (var c = 1; c <= maxCycles; c++) {
                var stageInfo = cycleMap[c];
                var cls = '';
                var label = '';

                if (stageInfo) {
                    if (stageInfo.hazard) {
                        cls = 'pipeline-stall';
                        label = 'STALL';
                    } else {
                        cls = STAGE_COLORS[stageInfo.stage] || 'pipeline-active';
                        label = stageInfo.stage;
                    }
                }

                html += '<td class="' + cls + '">' + label + '</td>';
            }

            html += '</tr>';
        }

        // If no instructions, show placeholder
        if (pipelineState.length === 0) {
            html = '<tr><td colspan="' + (maxCycles + 1) + '" class="text-muted text-center">' +
                   'Нет инструкций для симуляции</td></tr>';
        }

        tableBody.innerHTML = html;
        updateRegisterDisplay();
    }

    function updateRegisterDisplay() {
        for (var i = 0; i < 16; i++) {
            var el = document.getElementById('reg-r' + i);
            if (el) {
                el.textContent = '0x' + registers['R' + i].toString(16).toUpperCase();
            }
        }
    }

    function simulateCycle() {
        currentCycle++;

        if (currentCycle > maxCycles) {
            stopPipeline();
            return;
        }

        renderPipeline();

        // Update registers randomly for visual feedback
        for (var i = 0; i < 4; i++) {
            var regIdx = Math.floor(Math.random() * 16);
            registers['R' + regIdx] = Math.floor(Math.random() * 256);
        }
        updateRegisterDisplay();
    }

    // ---- Public API (called from HTML onclick) ----

    window.startPipeline = function () {
        var textarea = document.querySelector('.code-input');
        if (!textarea) return;

        var rawText = textarea.value;
        instructions = parseInstructions(rawText);

        if (instructions.length === 0) {
            alert('Пожалуйста, введите хотя бы одну инструкцию.');
            return;
        }

        // Reset state
        currentCycle = 0;
        for (var i = 0; i < 16; i++) {
            registers['R' + i] = 0;
        }
        maxCycles = instructions.length + 5;
        if (maxCycles < 8) maxCycles = 8;

        buildPipeline(instructions);
        isRunning = true;
        isPaused = false;

        if (timerId) clearInterval(timerId);
        timerId = setInterval(function () {
            if (!isPaused && isRunning) {
                if (currentCycle >= maxCycles) {
                    stopPipeline();
                } else {
                    simulateCycle();
                }
            }
        }, simSpeed);

        // Immediate first render
        simulateCycle();
    };

    window.pausePipeline = function () {
        isPaused = !isPaused;
        var btn = document.querySelector('.btn-warning');
        if (btn) {
            if (isPaused) {
                btn.innerHTML = '<i class="bi bi-play-fill me-1"></i>Продолжить';
            } else {
                btn.innerHTML = '<i class="bi bi-pause-fill me-1"></i>Пауза';
            }
        }
    };

    window.stepPipeline = function () {
        if (!isRunning) {
            // Initialize if not running
            var textarea = document.querySelector('.code-input');
            if (textarea) {
                instructions = parseInstructions(textarea.value);
                if (instructions.length === 0) return;
                currentCycle = 0;
                maxCycles = instructions.length + 5;
                buildPipeline(instructions);
                isRunning = true;
            }
        }
        if (currentCycle < maxCycles) {
            simulateCycle();
        } else {
            alert('Симуляция завершена. Нажмите "Сброс" для перезапуска.');
        }
    };

    window.resetPipeline = function () {
        if (timerId) {
            clearInterval(timerId);
            timerId = null;
        }
        isRunning = false;
        isPaused = false;
        currentCycle = 0;
        for (var i = 0; i < 16; i++) {
            registers['R' + i] = 0;
        }
        instructions = [];
        pipelineState = [];

        var tableBody = document.getElementById('pipelineBody');
        if (tableBody) {
            tableBody.innerHTML = '<tr><td colspan="' + (maxCycles + 1) + '" class="text-muted text-center">' +
                                  'Нажмите "Запустить" для начала симуляции</td></tr>';
        }
        updateRegisterDisplay();

        // Reset pause button text
        var btn = document.querySelector('.btn-warning');
        if (btn) {
            btn.innerHTML = '<i class="bi bi-pause-fill me-1"></i>Пауза';
        }

        console.log('Pipeline reset');
    };

    window.showPipelineHelp = function () {
        var helpText =
            '=== ИНСТРУКЦИЯ ПО РАБОТЕ С СИМУЛЯТОРОМ КОНВЕЙЕРА ===\n\n' +
            'Данный инструмент визуализирует 5-ступенчатый конвейер RISC-процессора:\n' +
            '  IF  — Выборка инструкции (Instruction Fetch)\n' +
            '  ID  — Декодирование (Instruction Decode)\n' +
            '  EX  — Выполнение (Execute)\n' +
            '  MEM — Доступ к памяти (Memory Access)\n' +
            '  WB  — Запись результата (Write Back)\n\n' +
            'Цветовая маркировка:\n' +
            '  🟢 Зеленый — Активная стадия (нормальное выполнение)\n' +
            '  🔴 Красный  — Конвейерная задержка / конфликт данных\n' +
            '  🔵 Синий    — Завершенная операция записи\n\n' +
            'Управление:\n' +
            '  ▶ Запустить — Начать полную симуляцию\n' +
            '  ⏸ Пауза — Приостановить / продолжить\n' +
            '  ⏭ Шаг — Выполнить один такт\n' +
            '  🔄 Сброс — Сбросить состояние симулятора\n\n' +
            'Формат инструкций:\n' +
            '  ADD R1, R2, R3   — Сложение: R1 = R2 + R3\n' +
            '  SUB R1, R2, R3   — Вычитание\n' +
            '  LW R1, 0(R2)     — Загрузка из памяти\n' +
            '  SW R1, 0(R2)     — Сохранение в память\n' +
            '  BEQ R1, R2, метка — Условный переход\n' +
            '  NOP              — Нет операции\n' +
            '  (строки, начинающиеся с ; или #, игнорируются)\n';

        alert(helpText);
    };

    // ---- Auto-init ----
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    console.log('Pipeline.js loaded — RISC Pipeline Visualizer');

})();


/* ===== simulator_numbers.js ===== */
/**
 * SIMULATOR: Number System Calculator
 * 
 * Real-time conversion between Decimal, Binary, and Hexadecimal.
 * Shows bit representation, signed/unsigned values, and common prefixes.
 */

(function () {
    'use strict';

    function init() {
        var container = document.querySelector('[data-simulator="numbers"]');
        if (!container) return;

        console.log('Numbers Simulator initialized');

        var decInput = container.querySelector('.num-dec-input');
        var binInput = container.querySelector('.num-bin-input');
        var hexInput = container.querySelector('.num-hex-input');
        var bitsDisplay = container.querySelector('.num-bits-display');
        var signedVal = container.querySelector('.num-signed-val');
        var unsignedVal = container.querySelector('.num-unsigned-val');
        var binWeight = container.querySelector('.num-bits-weights');

        function updateFromDec(value) {
            var num = parseInt(value, 10);
            if (isNaN(num)) {
                binInput.value = '';
                hexInput.value = '';
                if (bitsDisplay) bitsDisplay.innerHTML = '';
                if (signedVal) signedVal.textContent = '—';
                if (unsignedVal) unsignedVal.textContent = '—';
                if (binWeight) binWeight.innerHTML = '';
                return;
            }

            // Clamp to 16-bit signed range for display
            num = Math.max(-32768, Math.min(65535, num));

            var unsigned = num & 0xFFFF;
            var signed = unsigned > 32767 ? unsigned - 65536 : unsigned;

            binInput.value = unsigned.toString(2).padStart(16, '0');
            hexInput.value = '0x' + unsigned.toString(16).toUpperCase().padStart(4, '0');

            if (signedVal) signedVal.textContent = signed;
            if (unsignedVal) unsignedVal.textContent = unsigned;

            // Render bit visualization
            if (bitsDisplay) {
                var bits = unsigned.toString(2).padStart(16, '0');
                var html = '';
                for (var i = 0; i < bits.length; i++) {
                    var isSet = bits[i] === '1';
                    html += '<div class="num-bit ' + (isSet ? 'bit-set' : 'bit-clear') + '" title="Bit ' + (15 - i) + '">' +
                            bits[i] + '</div>';
                }
                bitsDisplay.innerHTML = html;

                // Bit labels
                var labels = '';
                for (var i = 15; i >= 0; i--) {
                    labels += '<div class="num-bit-label">' + i + '</div>';
                }
                if (binWeight) binWeight.innerHTML = labels;
            }
        }

        function updateFromBin(value) {
            // Remove non-binary chars
            var clean = value.replace(/[^01]/g, '');
            if (clean.length > 16) clean = clean.slice(-16);
            binInput.value = clean;

            var num = parseInt(clean, 2);
            if (isNaN(num) || clean.length === 0) {
                decInput.value = '';
                hexInput.value = '';
                return;
            }
            decInput.value = num.toString(10);
            updateFromDec(decInput.value);
        }

        function updateFromHex(value) {
            var clean = value.replace(/[^0-9A-Fa-f]/g, '');
            if (clean.length > 4) clean = clean.slice(-4);
            hexInput.value = '0x' + clean.toUpperCase();

            var num = parseInt(clean, 16);
            if (isNaN(num) || clean.length === 0) {
                decInput.value = '';
                binInput.value = '';
                return;
            }
            decInput.value = num.toString(10);
            updateFromDec(decInput.value);
        }

        // Event listeners
        decInput.addEventListener('input', function () {
            updateFromDec(this.value);
        });

        binInput.addEventListener('input', function () {
            updateFromBin(this.value);
        });

        hexInput.addEventListener('input', function () {
            var val = this.value.replace(/^0x/i, '');
            updateFromHex(val);
        });

        // Quick number buttons
        var quickBtns = container.querySelectorAll('.num-quick-btn');
        quickBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                decInput.value = this.dataset.value;
                updateFromDec(decInput.value);
            });
        });

        // Initialize with 0
        updateFromDec('0');
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    console.log('Numbers Simulator loaded');

})();


/* ===== simulator_riscv.js ===== */
/**
 * SIMULATOR: RISC-V Assembler / Emulator
 * 
 * Interactive RISC-V (RV32I subset) emulator with:
 * - Code editor for assembly instructions
 * - 32-register file display
 * - Step-by-step execution
 * - Memory view (stack + data)
 * - Supported: ADD, SUB, ADDI, LW, SW, BEQ, BNE, JAL, J, NOP, LI, AND, OR, XOR, SLL, SRL, JALR
 */

(function () {
    'use strict';

    var RegNames = [
        'zero','ra','sp','gp','tp','t0','t1','t2','s0','s1',
        'a0','a1','a2','a3','a4','a5','a6','a7','s2','s3',
        's4','s5','s6','s7','s8','s9','s10','s11','t3','t4','t5','t6'
    ];
    var RegAliases = {
        'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
        't0': 5, 't1': 6, 't2': 7, 's0': 8, 's1': 9,
        'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15,
        'a6': 16, 'a7': 17, 's2': 18, 's3': 19, 's4': 20, 's5': 21,
        's6': 22, 's7': 23, 's8': 24, 's9': 25, 's10': 26, 's11': 27,
        't3': 28, 't4': 29, 't5': 30, 't6': 31
    };

    // State
    var regs = new Array(32).fill(0);
    var pc = 0;
    var memory = {};
    var instructions = [];
    var labels = {};
    var programData = [];
    var dataSection = {};
    var currentInstrIdx = 0;
    var isRunning = false;
    var isPaused = false;
    var timerId = null;
    var maxSteps = 200;
    var stepCount = 0;
    var outputLog = [];
    var executedCount = 0;

    function init() {
        var container = document.querySelector('[data-simulator="riscv"]');
        if (!container) return;
        console.log('RISC-V Simulator initialized');
        resetState();
        renderRegisters(container);
        renderMemory(container);
    }

    function resetState() {
        regs = new Array(32).fill(0);
        regs[2] = 0x1000; // sp = 0x1000
        pc = 0;
        memory = { 0x1000: 0 };
        instructions = [];
        labels = {};
        programData = [];
        dataSection = {};
        currentInstrIdx = 0;
        stepCount = 0;
        executedCount = 0;
        outputLog = [];
    }

    function parseReg(name) {
        name = name.toLowerCase().replace(/[^a-z0-9]/g, '');
        if (name.startsWith('x')) {
            var idx = parseInt(name.substring(1), 10);
            if (idx >= 0 && idx <= 31) return idx;
        }
        if (RegAliases[name] !== undefined) return RegAliases[name];
        var num = parseInt(name, 10);
        if (num >= 0 && num <= 31) return num;
        return -1;
    }

    function parseImmediate(str) {
        str = str.replace(/\s/g, '');
        if (str.startsWith('0x')) return parseInt(str, 16);
        if (str.startsWith('0b')) return parseInt(str.substring(2), 2);
        return parseInt(str, 10);
    }

    function parseInstruction(line, lineNum) {
        line = line.trim();
        if (!line || line.startsWith('#') || line.startsWith(';')) return null;

        // Label?
        var labelMatch = line.match(/^([a-zA-Z_][a-zA-Z0-9_]*):/);
        if (labelMatch) {
            labels[labelMatch[1]] = lineNum;
            var rest = line.substring(labelMatch[0].length).trim();
            if (!rest) return null;
            line = rest;
        }

        // Remove comments
        line = line.replace(/#.*$/, '').replace(/;.*$/, '').trim();
        if (!line) return null;

        var parts = line.split(/\s+/);
        var opcode = parts[0].toLowerCase();

        // Handle .data section
        if (opcode === '.data') return { type: 'directive', opcode: '.data' };
        if (opcode === '.text') return { type: 'directive', opcode: '.text' };
        if (opcode === '.word') {
            var val = parseImmediate(parts[1]);
            programData.push(val);
            return { type: 'directive', opcode: '.word', value: val };
        }
        if (opcode === '.asciiz') {
            var str = line.match(/"(.*?)"/);
            if (str) {
                for (var c = 0; c < str[1].length; c++) {
                    programData.push(str[1].charCodeAt(c));
                }
                programData.push(0); // null terminator
            }
            return { type: 'directive', opcode: '.asciiz' };
        }

        var rest = line.substring(opcode.length).trim();
        var args = rest ? rest.split(',').map(function (a) { return a.trim(); }) : [];

        return { type: 'instruction', opcode: opcode, args: args, raw: line };
    }

    function assemble(code) {
        instructions = [];
        labels = {};
        programData = [];
        var lines = code.split('\n');
        var instrIdx = 0;
        var inData = false;

        for (var i = 0; i < lines.length; i++) {
            var line = lines[i].trim();
            if (!line || line.startsWith('#') || line.startsWith(';')) continue;

            if (line.toLowerCase().startsWith('.data')) { inData = true; continue; }
            if (line.toLowerCase().startsWith('.text')) { inData = false; continue; }

            if (inData) {
                var dw = line.match(/\.word\s+(.+)/);
                if (dw) {
                    var vals = dw[1].split(',').map(function (x) { return parseImmediate(x.trim()); });
                    programData = programData.concat(vals);
                }
                var asciiz = line.match(/\.asciiz\s+"(.*?)"/);
                if (asciiz) {
                    for (var c = 0; c < asciiz[1].length; c++) {
                        programData.push(asciiz[1].charCodeAt(c));
                    }
                    programData.push(0);
                }
                continue;
            }

            // Check for label
            var labelMatch = line.match(/^([a-zA-Z_][a-zA-Z0-9_]*):/);
            if (labelMatch) {
                labels[labelMatch[1]] = instrIdx;
                var rest = line.substring(labelMatch[0].length).trim();
                if (!rest) continue;
                line = rest;
            }

            var result = parseInstruction(line, instrIdx);
            if (result && result.type === 'instruction') {
                instructions.push(result);
                instrIdx++;
            }
        }

        // Load data section into memory
        var dataAddr = 0x2000;
        for (var d = 0; d < programData.length; d++) {
            memory[dataAddr + d * 4] = programData[d];
        }
        dataSection = { address: dataAddr, size: programData.length };
    }

    function executeNext(container) {
        if (currentInstrIdx >= instructions.length) {
            outputLog.push('  Программа завершена (PC выходит за границы)');
            renderLog(container);
            stop();
            return false;
        }

        var instr = instructions[currentInstrIdx];
        if (!instr) {
            currentInstrIdx++;
            return true;
        }

        var success = executeInstr(instr, container);
        if (success === false) {
            stop();
            return false;
        }

        currentInstrIdx++;
        executedCount++;
        stepCount++;

        if (stepCount >= maxSteps) {
            outputLog.push('  Достигнут лимит шагов (' + maxSteps + ')');
            renderLog(container);
            stop();
            return false;
        }

        return true;
    }

    function executeInstr(instr, container) {
        var op = instr.opcode;
        var args = instr.args;

        try {
            switch (op) {
                case 'nop': return true;
                case 'add': {
                    var rd = parseReg(args[0]);
                    var rs1 = parseReg(args[1]);
                    var rs2 = parseReg(args[2]);
                    if (rd < 0 || rs1 < 0 || rs2 < 0) { throw new Error('Invalid register in ADD'); }
                    if (rd === 0) return true;
                    regs[rd] = (regs[rs1] + regs[rs2]) | 0;
                    return true;
                }
                case 'sub': {
                    var rd = parseReg(args[0]);
                    var rs1 = parseReg(args[1]);
                    var rs2 = parseReg(args[2]);
                    if (rd < 0 || rs1 < 0 || rs2 < 0) { throw new Error('Invalid register in SUB'); }
                    if (rd === 0) return true;
                    regs[rd] = (regs[rs1] - regs[rs2]) | 0;
                    return true;
                }
                case 'addi': {
                    var rd = parseReg(args[0]);
                    var rs1 = parseReg(args[1]);
                    var imm = parseImmediate(args[2]);
                    if (rd < 0 || rs1 < 0 || isNaN(imm)) { throw new Error('Invalid ADDI'); }
                    if (rd === 0) return true;
                    regs[rd] = (regs[rs1] + imm) | 0;
                    return true;
                }
                case 'and': {
                    var rd = parseReg(args[0]);
                    var rs1 = parseReg(args[1]);
                    var rs2 = parseReg(args[2]);
                    if (rd === 0) return true;
                    regs[rd] = regs[rs1] & regs[rs2];
                    return true;
                }
                case 'or': {
                    var rd = parseReg(args[0]);
                    var rs1 = parseReg(args[1]);
                    var rs2 = parseReg(args[2]);
                    if (rd === 0) return true;
                    regs[rd] = regs[rs1] | regs[rs2];
                    return true;
                }
                case 'xor': {
                    var rd = parseReg(args[0]);
                    var rs1 = parseReg(args[1]);
                    var rs2 = parseReg(args[2]);
                    if (rd === 0) return true;
                    regs[rd] = regs[rs1] ^ regs[rs2];
                    return true;
                }
                case 'sll': {
                    var rd = parseReg(args[0]);
                    var rs1 = parseReg(args[1]);
                    var shamt = parseReg(args[2]);
                    if (rd === 0) return true;
                    regs[rd] = regs[rs1] << (regs[shamt] & 0x1F);
                    return true;
                }
                case 'srl': {
                    var rd = parseReg(args[0]);
                    var rs1 = parseReg(args[1]);
                    var shamt = parseReg(args[2]);
                    if (rd === 0) return true;
                    regs[rd] = (regs[rs1] >>> (regs[shamt] & 0x1F)) | 0;
                    return true;
                }
                case 'lw': {
                    var rd = parseReg(args[0]);
                    // Parse: LW R1, 8(R2) or LW R1, (R2)
                    var memMatch = args[1].match(/(?:(-?\d+))?\s*\(\s*(x?\d+|ra|sp|gp|tp|zero|[a-z][0-9]?)\s*\)/);
                    if (!memMatch) { throw new Error('Invalid LW format: ' + args[1]); }
                    var offset = memMatch[1] ? parseInt(memMatch[1]) : 0;
                    var baseR = parseReg(memMatch[2]);
                    if (rd < 0 || baseR < 0) { throw new Error('Invalid register in LW'); }
                    var addr = regs[baseR] + offset;
                    regs[rd] = memory[addr] !== undefined ? memory[addr] : 0;
                    return true;
                }
                case 'sw': {
                    var rs2 = parseReg(args[0]);
                    var memMatch = args[1].match(/(?:(-?\d+))?\s*\(\s*(x?\d+|ra|sp|gp|tp|zero|[a-z][0-9]?)\s*\)/);
                    if (!memMatch) { throw new Error('Invalid SW format: ' + args[1]); }
                    var offset = memMatch[1] ? parseInt(memMatch[1]) : 0;
                    var baseR = parseReg(memMatch[2]);
                    if (rs2 < 0 || baseR < 0) { throw new Error('Invalid register in SW'); }
                    var addr = regs[baseR] + offset;
                    memory[addr] = regs[rs2];
                    return true;
                }
                case 'li': {
                    var rd = parseReg(args[0]);
                    var imm = parseImmediate(args[1]);
                    if (rd < 0 || isNaN(imm)) { throw new Error('Invalid LI'); }
                    if (rd === 0) return true;
                    regs[rd] = imm;
                    return true;
                }
                case 'beq': {
                    var rs1 = parseReg(args[0]);
                    var rs2 = parseReg(args[1]);
                    var targetLabel = args[2];
                    if (regs[rs1] === regs[rs2]) {
                        if (labels[targetLabel] !== undefined) {
                            currentInstrIdx = labels[targetLabel] - 1;
                        }
                    }
                    return true;
                }
                case 'bne': {
                    var rs1 = parseReg(args[0]);
                    var rs2 = parseReg(args[1]);
                    var targetLabel = args[2];
                    if (regs[rs1] !== regs[rs2]) {
                        if (labels[targetLabel] !== undefined) {
                            currentInstrIdx = labels[targetLabel] - 1;
                        }
                    }
                    return true;
                }
                case 'jal': {
                    var rd = args.length > 1 ? parseReg(args[0]) : 1;
                    var targetLabel = args.length > 1 ? args[1] : args[0];
                    if (rd === undefined || rd < 0) rd = 1;
                    if (rd !== 0) regs[rd] = (currentInstrIdx + 1) * 4;
                    if (labels[targetLabel] !== undefined) {
                        currentInstrIdx = labels[targetLabel] - 1;
                    }
                    return true;
                }
                case 'j': {
                    var targetLabel = args[0];
                    if (labels[targetLabel] !== undefined) {
                        currentInstrIdx = labels[targetLabel] - 1;
                    }
                    return true;
                }
                case 'jalr': {
                    var rd = parseReg(args[0]);
                    var rs1 = parseReg(args[1]);
                    var imm = args.length > 2 ? parseImmediate(args[2]) : 0;
                    if (rd === undefined || rd < 0) rd = 0;
                    var targetAddr = (regs[rs1] + imm) | 0;
                    if (rd !== 0) regs[rd] = (currentInstrIdx + 1) * 4;
                    // JALR: set PC to target
                    var targetIdx = Math.floor(targetAddr / 4);
                    if (targetIdx >= 0 && targetIdx < instructions.length) {
                        currentInstrIdx = targetIdx - 1;
                    }
                    return true;
                }
                case 'ecall': {
                    var a7 = regs[17];
                    if (a7 === 1) { // print int
                        outputLog.push('  [OUT] ' + regs[10]);
                    } else if (a7 === 4) { // print string
                        var addr = regs[10];
                        var str = '';
                        while (memory[addr] && memory[addr] !== 0) {
                            str += String.fromCharCode(memory[addr]);
                            addr++;
                        }
                        outputLog.push('  [OUT] ' + str);
                    } else if (a7 === 10) { // exit
                        outputLog.push('  Программа завершена (ecall exit)');
                        renderLog(container);
                        stop();
                        return false;
                    }
                    return true;
                }
                case 'ret': {
                    // ret = jalr zero, ra, 0
                    if (regs[1] !== undefined) {
                        var retIdx = Math.floor(regs[1] / 4);
                        if (retIdx >= 0 && retIdx < instructions.length) {
                            currentInstrIdx = retIdx - 1;
                        }
                    }
                    return true;
                }
                case 'mv': {
                    var rd = parseReg(args[0]);
                    var rs1 = parseReg(args[1]);
                    if (rd === 0) return true;
                    regs[rd] = regs[rs1];
                    return true;
                }
                default:
                    outputLog.push('  [WARN] Неподдерживаемая инструкция: ' + op);
                    renderLog(container);
                    return true;
            }
        } catch (e) {
            outputLog.push('  [ERROR] ' + e.message + ' в строке: ' + instr.raw);
            renderLog(container);
            return false;
        }
    }

    function renderRegisters(container) {
        var display = container.querySelector('.riscv-regs-body');
        if (!display) return;
        var html = '';
        for (var i = 0; i < 32; i += 4) {
            html += '<div class="riscv-reg-row">';
            for (var j = 0; j < 4; j++) {
                var idx = i + j;
                var val = regs[idx];
                var valHex = (val >>> 0).toString(16).toUpperCase().padStart(8, '0');
                var changed = executedCount > 0 ? '' : '';
                html += '<div class="riscv-reg-cell">' +
                        '<span class="reg-name">' + RegNames[idx] + '</span>' +
                        '<span class="reg-val">0x' + valHex + '</span>' +
                        '<span class="reg-val-dec">' + val + '</span>' +
                        '</div>';
            }
            html += '</div>';
        }
        display.innerHTML = html;

        // Update PC
        var pcEl = container.querySelector('.riscv-pc-val');
        if (pcEl) pcEl.textContent = '0x' + (currentInstrIdx * 4).toString(16).toUpperCase().padStart(4, '0');
    }

    function renderMemory(container) {
        var memDisplay = container.querySelector('.riscv-mem-body');
        if (!memDisplay) return;
        var addrs = Object.keys(memory).sort(function (a, b) { return parseInt(a) - parseInt(b); });
        if (addrs.length === 0) {
            memDisplay.innerHTML = '<div class="text-muted p-2">Память не используется</div>';
            return;
        }
        var html = '';
        var count = 0;
        for (var i = 0; i < addrs.length && count < 16; i++) {
            var addr = parseInt(addrs[i]);
            var val = memory[addr];
            html += '<div class="riscv-mem-row">' +
                    '<span class="mem-addr">0x' + addr.toString(16).toUpperCase().padStart(4, '0') + '</span>' +
                    '<span class="mem-val">0x' + (val >>> 0).toString(16).toUpperCase().padStart(8, '0') + '</span>' +
                    '</div>';
            count++;
        }
        if (addrs.length > 16) {
            html += '<div class="text-muted p-1" style="font-size:0.8rem">... и ещё ' + (addrs.length - 16) + ' адресов</div>';
        }
        memDisplay.innerHTML = html;
    }

    function renderLog(container) {
        var logEl = container.querySelector('.riscv-log');
        if (!logEl) return;
        logEl.innerHTML = outputLog.map(function (l) { return '<div>' + l + '</div>'; }).join('');
        logEl.scrollTop = logEl.scrollHeight;
    }

    function renderCodeHighlight(container) {
        var codeLines = container.querySelectorAll('.riscv-code-line');
        codeLines.forEach(function (el, idx) {
            el.classList.remove('code-active', 'code-done');
            if (idx === currentInstrIdx && idx < instructions.length) {
                el.classList.add('code-active');
            } else if (idx < currentInstrIdx && idx < instructions.length) {
                el.classList.add('code-done');
            }
        });
    }

    // Public API
    window.runRiscv = function () {
        var container = document.querySelector('[data-simulator="riscv"]');
        if (!container) return;
        var codeEl = container.querySelector('.riscv-code-input');
        if (!codeEl) return;

        resetState();
        outputLog = [];
        assemble(codeEl.value);

        if (instructions.length === 0) {
            outputLog.push('  Нет инструкций для выполнения');
            renderLog(container);
            return;
        }

        outputLog.push('  Assembled ' + instructions.length + ' instructions');
        isRunning = true;
        isPaused = false;
        stepCount = 0;

        if (timerId) clearInterval(timerId);
        timerId = setInterval(function () {
            if (!isPaused && isRunning) {
                var cont = executeNext(container);
                renderRegisters(container);
                renderMemory(container);
                renderCodeHighlight(container);
                if (!cont) {
                    outputLog.push('  Симуляция завершена (' + executedCount + ' инструкций выполнено)');
                    renderLog(container);
                    stop();
                }
            }
        }, 500);
    };

    window.stepRiscv = function () {
        var container = document.querySelector('[data-simulator="riscv"]');
        if (!container) return;
        var codeEl = container.querySelector('.riscv-code-input');
        if (!codeEl) return;

        if (!isRunning) {
            resetState();
            outputLog = [];
            assemble(codeEl.value);
            if (instructions.length === 0) return;
            outputLog.push('  Assembled ' + instructions.length + ' instructions');
            isRunning = true;
        }

        executeNext(container);
        renderRegisters(container);
        renderMemory(container);
        renderCodeHighlight(container);
        renderLog(container);
    };

    window.resetRiscv = function () {
        if (timerId) { clearInterval(timerId); timerId = null; }
        var container = document.querySelector('[data-simulator="riscv"]');
        if (!container) return;
        resetState();
        outputLog = [];
        renderRegisters(container);
        renderMemory(container);
        renderLog(container);

        var codeLines = container.querySelectorAll('.riscv-code-line');
        codeLines.forEach(function (el) { el.classList.remove('code-active', 'code-done'); });

        isRunning = false;
        isPaused = false;
    };

    window.pauseRiscv = function () {
        isPaused = !isPaused;
        var container = document.querySelector('[data-simulator="riscv"]');
        if (!container) return;
        var btn = container.querySelector('.riscv-pause-btn');
        if (btn) {
            btn.innerHTML = isPaused ? '<i class="bi bi-play-fill"></i> Продолжить' : '<i class="bi bi-pause-fill"></i> Пауза';
        }
    };

    window.loadRiscvExample = function (name) {
        var container = document.querySelector('[data-simulator="riscv"]');
        if (!container) return;
        var codeEl = container.querySelector('.riscv-code-input');
        if (!codeEl) return;

        var examples = {
            'add': '# Пример: сложение двух чисел\naddi  a0, zero, 5    # a0 = 5\naddi  a1, zero, 3    # a1 = 3\nadd   a2, a0, a1     # a2 = a0 + a1 = 8',
            'loop': '# Пример: цикл\n      addi  t0, zero, 0     # t0 = 0 (counter)\n      addi  t1, zero, 5     # t1 = 5 (limit)\nloop: addi  t0, t0, 1       # t0++\n      bne   t0, t1, loop    # if (t0 != t1) goto loop\n      # t0 = 5 после цикла',
            'mem': '# Пример: работа с памятью\n      addi  sp, sp, -16      # Выделить место в стеке\n      addi  t0, zero, 42     # t0 = 42\n      sw    t0, 0(sp)        # Сохранить t0 в стек\n      lw    t1, 0(sp)        # Загрузить обратно в t1\n      addi  sp, sp, 16       # Восстановить стек',
            'func': '# Пример: функция\n      jal   func             # Вызов функции\n      j     end               # Переход к концу\nfunc: addi  t0, zero, 99     # t0 = 99\n      jr    ra                # Возврат\nend:  nop                     # Конец программы'
        };

        if (examples[name]) {
            codeEl.value = examples[name];
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    console.log('RISC-V Simulator loaded');

})();


/* ===== simulator_cache.js ===== */
/**
 * SIMULATOR: Cache Memory Visualizer
 * 
 * Interactive cache simulation with:
 * - Configurable: number of sets, ways, block size
 * - Visual grid showing cache lines with colors
 * - LRU / FIFO / Random replacement policies
 * - Hit/miss tracking with counters
 * - Memory address input for read/write operations
 */

(function () {
    'use strict';

    var cache = {};
    var sets = 4;
    var ways = 2;
    var blockSize = 4;
    var policy = 'LRU';
    var hits = 0;
    var misses = 0;
    var accessCount = 0;
    var currentAddr = 0;
    var history = [];

    function init() {
        var container = document.querySelector('[data-simulator="cache"]');
        if (!container) return;
        console.log('Cache Simulator initialized');
        resetCache(container);
        setupControls(container);
    }

    function updateConfig(container) {
        sets = parseInt(container.querySelector('.cache-sets').value) || 4;
        ways = parseInt(container.querySelector('.cache-ways').value) || 2;
        blockSize = parseInt(container.querySelector('.cache-block-size').value) || 4;
        policy = container.querySelector('.cache-policy').value || 'LRU';
        resetCache(container);
    }

    function resetCache(container) {
        cache = {};
        hits = 0;
        misses = 0;
        accessCount = 0;
        history = [];
        for (var s = 0; s < sets; s++) {
            cache[s] = [];
            for (var w = 0; w < ways; w++) {
                cache[s][w] = { tag: -1, valid: false, dirty: false, lru: 0, data: '' };
            }
        }
        renderCache(container);
        updateStats(container);
    }

    function getSetIndex(addr) {
        var blockAddr = Math.floor(addr / blockSize);
        return blockAddr % sets;
    }

    function getTag(addr) {
        var blockAddr = Math.floor(addr / blockSize);
        return Math.floor(blockAddr / sets);
    }

    function accessMemory(addr, isWrite, container) {
        currentAddr = addr;
        var setIdx = getSetIndex(addr);
        var tag = getTag(addr);
        var set = cache[setIdx];
        accessCount++;
        var hit = false;

        // Check for hit
        for (var w = 0; w < set.length; w++) {
            if (set[w].valid && set[w].tag === tag) {
                hit = true;
                set[w].lru = accessCount;
                if (isWrite) set[w].dirty = true;
                break;
            }
        }

        if (hit) {
            hits++;
            history.unshift({ addr: addr, result: 'HIT', set: setIdx, way: w });
        } else {
            misses++;
            // Find replacement victim
            var victimWay = findVictim(set, container);
            set[victimWay].tag = tag;
            set[victimWay].valid = true;
            set[victimWay].dirty = isWrite;
            set[victimWay].lru = accessCount;
            set[victimWay].data = '0x' + addr.toString(16).toUpperCase();
            history.unshift({ addr: addr, result: 'MISS', set: setIdx, way: victimWay, evicted: set[victimWay].valid && set[victimWay].tag !== tag });
        }

        // Keep history short
        if (history.length > 20) history.pop();

        renderCache(container);
        updateStats(container);
        renderHistory(container);

        // Flash effect
        var cell = container.querySelector('.cache-cell[data-set="' + setIdx + '"][data-way="' + (hit ? w : history[0].way) + '"]');
        if (cell) {
            cell.classList.add('cache-flash');
            setTimeout(function () { cell.classList.remove('cache-flash'); }, 500);
        }
    }

    function findVictim(set) {
        if (policy === 'LRU') {
            var minLru = Infinity;
            var victim = 0;
            for (var w = 0; w < set.length; w++) {
                if (!set[w].valid) return w;
                if (set[w].lru < minLru) {
                    minLru = set[w].lru;
                    victim = w;
                }
            }
            return victim;
        } else if (policy === 'FIFO') {
            // Simple: use LRU counter as age
            var minLru = Infinity;
            var victim = 0;
            for (var w = 0; w < set.length; w++) {
                if (!set[w].valid) return w;
                if (set[w].lru < minLru) {
                    minLru = set[w].lru;
                    victim = w;
                }
            }
            return victim;
        } else { // Random
            return Math.floor(Math.random() * set.length);
        }
    }

    function renderCache(container) {
        var grid = container.querySelector('.cache-grid');
        if (!grid) return;

        var html = '';

        // Header row with set indices
        html += '<div class="cache-row cache-header">';
        html += '<div class="cache-cell cache-label">Set \\ Way</div>';
        for (var w = 0; w < ways; w++) {
            html += '<div class="cache-cell cache-way-label">Way ' + w + '</div>';
        }
        html += '</div>';

        for (var s = 0; s < sets; s++) {
            html += '<div class="cache-row">';
            html += '<div class="cache-cell cache-set-label">Set ' + s + '</div>';
            var set = cache[s];
            for (var w = 0; w < set.length; w++) {
                var line = set[w];
                var cssClass = 'cache-cell';
                if (!line.valid) {
                    cssClass += ' cache-invalid';
                } else if (line.dirty) {
                    cssClass += ' cache-dirty';
                } else {
                    cssClass += ' cache-valid';
                }
                var content = line.valid ? ('Tag: 0x' + line.tag.toString(16).toUpperCase()) : '—';
                html += '<div class="' + cssClass + '" data-set="' + s + '" data-way="' + w + '">' +
                        '<span class="cache-tag">' + content + '</span>' +
                        '</div>';
            }
            html += '</div>';
        }

        grid.innerHTML = html;
    }

    function updateStats(container) {
        var hitEl = container.querySelector('.cache-stats-hits');
        var missEl = container.querySelector('.cache-stats-misses');
        var rateEl = container.querySelector('.cache-stats-rate');
        var totalEl = container.querySelector('.cache-stats-total');

        if (totalEl) totalEl.textContent = accessCount;
        if (hitEl) hitEl.textContent = hits;
        if (missEl) missEl.textContent = misses;
        var rate = accessCount > 0 ? (hits / accessCount * 100).toFixed(1) : '0.0';
        if (rateEl) rateEl.textContent = rate + '%';
    }

    function renderHistory(container) {
        var histEl = container.querySelector('.cache-history');
        if (!histEl) return;
        var html = '';
        for (var i = 0; i < history.length; i++) {
            var h = history[i];
            var cls = h.result === 'HIT' ? 'text-success' : 'text-danger';
            html += '<div class="cache-history-item ' + cls + '">' +
                    '[' + h.result + '] 0x' + h.addr.toString(16).toUpperCase() +
                    ' → Set ' + h.set + ', Way ' + h.way +
                    '</div>';
        }
        histEl.innerHTML = html;
    }

    function setupControls(container) {
        var readBtn = container.querySelector('.cache-read-btn');
        var writeBtn = container.querySelector('.cache-write-btn');
        var resetBtn = container.querySelector('.cache-reset-btn');
        var addrInput = container.querySelector('.cache-addr-input');
        var configBtn = container.querySelector('.cache-config-btn');

        if (readBtn) {
            readBtn.addEventListener('click', function () {
                var addr = parseInt(addrInput.value, 16);
                if (isNaN(addr)) addr = parseInt(addrInput.value, 10);
                if (isNaN(addr) || addr < 0) addr = 0;
                accessMemory(addr, false, container);
            });
        }

        if (writeBtn) {
            writeBtn.addEventListener('click', function () {
                var addr = parseInt(addrInput.value, 16);
                if (isNaN(addr)) addr = parseInt(addrInput.value, 10);
                if (isNaN(addr) || addr < 0) addr = 0;
                accessMemory(addr, true, container);
            });
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', function () { resetCache(container); });
        }

        if (configBtn) {
            configBtn.addEventListener('click', function () { updateConfig(container); });
        }

        // Quick access buttons
        var quickBtns = container.querySelectorAll('.cache-quick-btn');
        quickBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                addrInput.value = this.dataset.addr;
                accessMemory(parseInt(this.dataset.addr, 16), this.dataset.op === 'write', container);
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    console.log('Cache Simulator loaded');

})();


/* ===== simulator_mesi.js ===== */
/**
 * SIMULATOR: MESI Cache Coherency Protocol
 * 
 * Interactive MESI protocol simulator with:
 * - 2-4 CPU cores with private caches
 * - Cache line states: Modified (M), Exclusive (E), Shared (S), Invalid (I)
 * - Bus transactions (BusRd, BusRdX, etc.)
 * - State transition diagram
 * - Step-by-step simulation of read/write operations
 */

(function () {
    'use strict';

    var MESI = { M: 'M', E: 'E', S: 'S', I: 'I' };
    var STATE_COLORS = {
        'M': '#dc3545',  // Red - Modified
        'E': '#28a745',  // Green - Exclusive
        'S': '#ffc107',  // Yellow - Shared
        'I': '#6c757d'   // Gray - Invalid
    };
    var STATE_LABELS = {
        'M': 'Modified',
        'E': 'Exclusive',
        'S': 'Shared',
        'I': 'Invalid'
    };

    var numCores = 2;
    var cacheLines = {};
    var busTransactions = [];
    var stepCount = 0;
    var currentAddr = 0;
    var memoryData = {};
    var coreRegs = {};
    var isAnimating = false;

    function init() {
        var container = document.querySelector('[data-simulator="mesi"]');
        if (!container) return;
        console.log('MESI Simulator initialized');
        resetSim(container);
        setupControls(container);
        renderTransitions(container);
    }

    function resetSim(container) {
        numCores = parseInt(container.querySelector('.mesi-cores').value) || 2;
        cacheLines = {};
        busTransactions = [];
        stepCount = 0;
        isAnimating = false;

        for (var c = 0; c < numCores; c++) {
            cacheLines[c] = {};
            coreRegs[c] = { reads: 0, writes: 0 };
        }

        // Initialize some memory blocks
        var addrs = [0x1000, 0x1004, 0x1008, 0x100C, 0x1010];
        for (var i = 0; i < addrs.length; i++) {
            memoryData[addrs[i]] = 0;
        }

        currentAddr = 0x1000;
        renderCaches(container);
        renderStats(container);
        renderBus(container);
        updateAddrDisplay(container);
    }

    function getAddrBlock(addr) {
        return addr & 0xFFF0; // 16-byte aligned block
    }

    function addBusTransaction(type, core, addr, detail) {
        busTransactions.unshift({
            type: type,
            core: core,
            addr: addr,
            detail: detail || '',
            step: stepCount
        });
        if (busTransactions.length > 15) busTransactions.pop();
    }

    function coreRead(core, addr, container) {
        if (isAnimating) return;
        stepCount++;
        currentAddr = addr;
        var block = getAddrBlock(addr);
        var lines = cacheLines[core];
        coreRegs[core].reads++;

        if (lines[block]) {
            var state = lines[block];
            if (state === 'M' || state === 'E' || state === 'S') {
                // Cache hit
                addBusTransaction('—', core, addr, 'Cache HIT (' + state + ')');
                renderCaches(container);
                renderStats(container);
                renderBus(container);
                highlightCore(core, container);
                return;
            }
        }

        // Cache miss — need to read from bus
        addBusTransaction('BusRd', core, addr, 'Read miss — requesting from bus');

        // Check other cores
        var sharedCopy = false;
        var otherModified = false;
        var modifiedCore = -1;

        for (var c = 0; c < numCores; c++) {
            if (c === core) continue;
            if (cacheLines[c][block]) {
                var s = cacheLines[c][block];
                if (s === 'M') {
                    otherModified = true;
                    modifiedCore = c;
                    // Write back to memory
                    addBusTransaction('BusRd / WB', c, addr, 'Core ' + c + ' writes back modified data');
                }
                if (s === 'S' || s === 'E') {
                    sharedCopy = true;
                }
            }
        }

        // Update states according to MESI protocol
        if (otherModified) {
            cacheLines[modifiedCore][block] = 'S';
            sharedCopy = true;
            addBusTransaction('BusRd / Snoop', modifiedCore, addr, 'Core ' + modifiedCore + ' transitions M→S');
        }

        lines[block] = sharedCopy ? 'S' : 'E';
        addBusTransaction('BusRd / Grant', core, addr, 'Core ' + core + ' gets ' + (sharedCopy ? 'Shared' : 'Exclusive') + ' copy');

        renderCaches(container);
        renderStats(container);
        renderBus(container);
        highlightCore(core, container);
        updateAddrDisplay(container);
    }

    function coreWrite(core, addr, container) {
        if (isAnimating) return;
        stepCount++;
        currentAddr = addr;
        var block = getAddrBlock(addr);
        var lines = cacheLines[core];
        coreRegs[core].writes++;

        if (lines[block]) {
            var state = lines[block];
            if (state === 'M') {
                // Write hit, already modified
                addBusTransaction('—', core, addr, 'Write HIT (M) — local write');
                renderCaches(container);
                renderStats(container);
                renderBus(container);
                highlightCore(core, container);
                return;
            }
            if (state === 'E') {
                // Write hit, exclusive -> modified
                lines[block] = 'M';
                addBusTransaction('—', core, addr, 'E→M — local write, now Modified');
                renderCaches(container);
                renderStats(container);
                renderBus(container);
                highlightCore(core, container);
                return;
            }
            if (state === 'S') {
                // Write hit on shared — need to invalidate others
                addBusTransaction('BusRdX', core, addr, 'Write to shared — invalidating other copies');
                for (var c = 0; c < numCores; c++) {
                    if (c === core) continue;
                    if (cacheLines[c][block]) {
                        cacheLines[c][block] = 'I';
                        addBusTransaction('BusRdX / Inv', c, addr, 'Core ' + c + ' S→I');
                    }
                }
                lines[block] = 'M';
                addBusTransaction('BusRdX / Grant', core, addr, 'Core ' + core + ' gets exclusive access (S→M)');
                renderCaches(container);
                renderStats(container);
                renderBus(container);
                highlightCore(core, container);
                return;
            }
        }

        // Write miss — need to get exclusive access
        addBusTransaction('BusRdX', core, addr, 'Write miss — requesting exclusive access');
        for (var c = 0; c < numCores; c++) {
            if (c === core) continue;
            if (cacheLines[c][block]) {
                var s = cacheLines[c][block];
                if (s === 'M' || s === 'E' || s === 'S') {
                    cacheLines[c][block] = 'I';
                    addBusTransaction('BusRdX / Inv', c, addr, 'Core ' + c + ' ' + s + '→I');
                }
            }
        }
        lines[block] = 'M';
        addBusTransaction('BusRdX / Grant', core, addr, 'Core ' + core + ' gets Modified copy');
        memoryData[block] = 1;

        renderCaches(container);
        renderStats(container);
        renderBus(container);
        highlightCore(core, container);
        updateAddrDisplay(container);
    }

    function renderCaches(container) {
        var grid = container.querySelector('.mesi-cache-grid');
        if (!grid) return;

        var html = '';

        // Header
        html += '<div class="mesi-row mesi-row-header">';
        html += '<div class="mesi-core-label mesi-cell">Core</div>';
        html += '<div class="mesi-state-cell mesi-cell">Адрес блока</div>';
        html += '<div class="mesi-state-cell mesi-cell">Состояние</div>';
        html += '<div class="mesi-state-cell mesi-cell">Значение</div>';
        html += '</div>';

        for (var c = 0; c < numCores; c++) {
            var lines = cacheLines[c];
            var blocks = Object.keys(lines);

            if (blocks.length === 0) {
                html += '<div class="mesi-row">';
                html += '<div class="mesi-core-label mesi-cell" data-core="' + c + '">Core ' + c + '</div>';
                html += '<div class="mesi-cell" colspan="3" style="grid-column:2/5;color:#888;">(кэш пуст)</div>';
                html += '</div>';
            } else {
                for (var b = 0; b < blocks.length; b++) {
                    var block = blocks[b];
                    var state = lines[block];
                    html += '<div class="mesi-row">';
                    html += '<div class="mesi-core-label mesi-cell" data-core="' + c + '">Core ' + c + '</div>';
                    html += '<div class="mesi-cell"><code>0x' + parseInt(block).toString(16).toUpperCase() + '</code></div>';
                    html += '<div class="mesi-cell">' +
                            '<span class="mesi-state-badge mesi-state-' + state + '" ' +
                            'style="background:' + STATE_COLORS[state] + '">' +
                            state + '</span></div>';
                    html += '<div class="mesi-cell">' + (memoryData[block] !== undefined ? memoryData[block] : '0') + '</div>';
                    html += '</div>';
                }
            }
        }

        grid.innerHTML = html;
    }

    function renderStats(container) {
        for (var c = 0; c < numCores; c++) {
            var readsEl = container.querySelector('.mesi-core-reads-' + c);
            var writesEl = container.querySelector('.mesi-core-writes-' + c);
            if (readsEl) readsEl.textContent = coreRegs[c].reads || 0;
            if (writesEl) writesEl.textContent = coreRegs[c].writes || 0;
        }
    }

    function renderBus(container) {
        var busEl = container.querySelector('.mesi-bus-log');
        if (!busEl) return;
        var html = '';
        for (var i = 0; i < busTransactions.length; i++) {
            var t = busTransactions[i];
            var color = t.type === 'BusRdX' ? '#dc3545' : (t.type === 'BusRd' ? '#0d6efd' : '#666');
            html += '<div class="mesi-bus-item">' +
                    '<span style="color:' + color + ';font-weight:600;">' + t.type + '</span> ' +
                    '<span class="text-muted">C' + t.core + '</span> ' +
                    '<code>0x' + t.addr.toString(16).toUpperCase() + '</code> ' +
                    '<span class="text-muted">— ' + t.detail + '</span>' +
                    '</div>';
        }
        busEl.innerHTML = html;
    }

    function renderTransitions(container) {
        var diagram = container.querySelector('.mesi-transition-diagram');
        if (!diagram) return;
        var html = '<div class="mesi-diagram-container">';
        html += '<svg viewBox="0 0 500 280" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-height:280px">';
        // States
        var states = [
            { name: 'M', x: 380, y: 40, color: STATE_COLORS.M, label: 'Modified' },
            { name: 'E', x: 380, y: 150, color: STATE_COLORS.E, label: 'Exclusive' },
            { name: 'S', x: 120, y: 150, color: STATE_COLORS.S, label: 'Shared' },
            { name: 'I', x: 120, y: 40, color: STATE_COLORS.I, label: 'Invalid' }
        ];

        // Arrows
        var arrows = [
            { from: 'I', to: 'E', label: 'BusRd / Miss' },
            { from: 'I', to: 'S', label: 'BusRd / Shared' },
            { from: 'E', to: 'M', label: 'Local Write' },
            { from: 'E', to: 'I', label: 'BusRdX (other)' },
            { from: 'S', to: 'M', label: 'BusRdX (local)' },
            { from: 'S', to: 'I', label: 'BusRdX (other)' },
            { from: 'M', to: 'S', label: 'BusRd (other)' },
            { from: 'M', to: 'I', label: 'BusRdX (other)' }
        ];

        // Draw arrows (simplified SVG lines)
        arrows.forEach(function (a) {
            var from = states.find(function (s) { return s.name === a.from; });
            var to = states.find(function (s) { return s.name === a.to; });
            if (!from || !to) return;
            var x1 = from.x, y1 = from.y, x2 = to.x, y2 = to.y;
            var midX = (x1 + x2) / 2;
            var midY = (y1 + y2) / 2;
            html += '<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 + '" ' +
                    'stroke="#999" stroke-width="1.5" marker-end="url(#arrowhead)"/>';
            html += '<text x="' + midX + '" y="' + (midY - 5) + '" text-anchor="middle" font-size="9" fill="#666">' +
                    a.label + '</text>';
        });

        // Draw state circles
        states.forEach(function (s) {
            html += '<circle cx="' + s.x + '" cy="' + s.y + '" r="28" fill="' + s.color + '" opacity="0.9"/>';
            html += '<text x="' + s.x + '" y="' + (s.y - 3) + '" text-anchor="middle" font-size="18" font-weight="bold" fill="#fff">' + s.name + '</text>';
            html += '<text x="' + s.x + '" y="' + (s.y + 14) + '" text-anchor="middle" font-size="8" fill="#fff" opacity="0.9">' + s.label + '</text>';
        });

        html += '<defs><marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#999"/></marker></defs>';
        html += '</svg></div>';
        diagram.innerHTML = html;
    }

    function highlightCore(core, container) {
        var labels = container.querySelectorAll('.mesi-core-label');
        labels.forEach(function (el) {
            el.classList.remove('mesi-core-active');
            if (el.dataset.core == core) {
                el.classList.add('mesi-core-active');
            }
        });
    }

    function updateAddrDisplay(container) {
        var el = container.querySelector('.mesi-current-addr');
        if (el) el.textContent = '0x' + currentAddr.toString(16).toUpperCase();
    }

    function setupControls(container) {
        var readBtns = container.querySelectorAll('.mesi-read-btn');
        var writeBtns = container.querySelectorAll('.mesi-write-btn');
        var resetBtn = container.querySelector('.mesi-reset-btn');
        var addrInput = container.querySelector('.mesi-addr-input');

        readBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                var core = parseInt(this.dataset.core);
                var addr = parseInt(addrInput.value, 16);
                if (isNaN(addr)) addr = 0x1000;
                coreRead(core, addr, container);
            });
        });

        writeBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                var core = parseInt(this.dataset.core);
                var addr = parseInt(addrInput.value, 16);
                if (isNaN(addr)) addr = 0x1000;
                coreWrite(core, addr, container);
            });
        });

        if (resetBtn) {
            resetBtn.addEventListener('click', function () { resetSim(container); });
        }

        var coreSelect = container.querySelector('.mesi-cores');
        if (coreSelect) {
            coreSelect.addEventListener('change', function () { resetSim(container); });
        }

        // Quick scenario buttons
        var scenarioBtns = container.querySelectorAll('.mesi-scenario-btn');
        scenarioBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                var scenario = this.dataset.scenario;
                resetSim(container);
                switch (scenario) {
                    case 'read-shared':
                        coreRead(0, 0x1000, container);
                        coreRead(1, 0x1000, container);
                        break;
                    case 'write-exclusive':
                        coreWrite(0, 0x1000, container);
                        break;
                    case 'write-invalidate':
                        coreRead(0, 0x1000, container);
                        coreRead(1, 0x1000, container);
                        coreWrite(0, 0x1000, container);
                        break;
                }
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    console.log('MESI Simulator loaded');

})();


