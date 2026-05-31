"""
Management command to populate the database with sample course data.
Creates 6 modules covering the Microprocessor Systems curriculum.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from course.models import Module, Section, Topic, Assignment, InteractiveElement, UserProgress

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполняет базу данных демонстрационными данными курса'

    def handle(self, *args, **options):
        self.stdout.write('Заполнение базы данных...')

        # Create or update admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Администратор',
                last_name='Системы',
            )
            self.stdout.write(self.style.SUCCESS('  Создан суперпользователь: admin / admin123'))

        # Create a demo student
        if not User.objects.filter(username='student').exists():
            student = User.objects.create_user(
                username='student',
                email='student@example.com',
                password='student123',
                first_name='Иван',
                last_name='Петров',
            )
            student.role = User.Role.STUDENT
            student.save()
            self.stdout.write(self.style.SUCCESS('  Создан студент: student / student123'))

        # Module 1: Introduction to Microprocessor Systems
        mod1, _ = Module.objects.get_or_create(
            order_number=1,
            defaults={
                'title': 'Введение в микропроцессорные системы',
                'description': 'Основные понятия, история развития, классификация микропроцессоров и области их применения.',
                'icon': 'cpu',
            }
        )
        self._create_section(mod1, 1, 'Основные понятия', [
            ('Что такое микропроцессор?', 8, self._intro_topic_1()),
            ('История развития микропроцессоров', 10, self._intro_topic_2()),
            ('Классификация и архитектуры', 10, self._intro_topic_3()),
        ])
        self._create_section(mod1, 2, 'Области применения', [
            ('Встраиваемые системы', 8, self._intro_topic_4()),
            ('Современные тенденции развития', 7, self._intro_topic_5()),
        ])

        # Module 2: Microprocessor Architecture
        mod2, _ = Module.objects.get_or_create(
            order_number=2,
            defaults={
                'title': 'Архитектура микропроцессоров',
                'description': 'Внутренняя структура, системы команд, регистровая архитектура и организация памяти.',
                'icon': 'motherboard',
            }
        )
        self._create_section(mod2, 1, 'Внутренняя структура МП', [
            ('АЛУ, УУ, регистры', 12, self._arch_topic_1()),
            ('Система команд', 15, self._arch_topic_2()),
        ])
        self._create_section(mod2, 2, 'Организация памяти', [
            ('Сегментная и страничная организация', 12, self._arch_topic_3()),
            ('Кэш-память', 10, self._arch_topic_4()),
        ])

        # Module 3: Instruction Pipeline
        mod3, _ = Module.objects.get_or_create(
            order_number=3,
            defaults={
                'title': 'Конвейерная обработка команд',
                'description': 'Принципы конвейеризации, конфликты и методы их разрешения.',
                'icon': 'signpost-2',
            }
        )
        self._create_section(mod3, 1, 'Основы конвейеризации', [
            ('Понятие конвейера', 10, self._pipe_topic_1()),
            ('5-ступенчатый конвейер RISC', 15, self._pipe_topic_2()),
        ])
        self._create_section(mod3, 2, 'Конфликты в конвейере', [
            ('Структурные конфликты', 12, self._pipe_topic_3()),
            ('Конфликты по данным', 15, self._pipe_topic_4()),
            ('Конфликты по управлению', 12, self._pipe_topic_5()),
        ])

        # Module 4: Memory Systems
        mod4, _ = Module.objects.get_or_create(
            order_number=4,
            defaults={
                'title': 'Организация памяти и ввод-вывод',
                'description': 'Иерархия памяти, контроллеры прерываний, прямой доступ к памяти.',
                'icon': 'memory',
            }
        )
        self._create_section(mod4, 1, 'Иерархия памяти', [
            ('Оперативная и постоянная память', 10, self._mem_topic_1()),
            ('Виртуальная память', 12, self._mem_topic_2()),
        ])
        self._create_section(mod4, 2, 'Система ввода-вывода', [
            ('Программный и прерывательный ввод-вывод', 12, self._mem_topic_3()),
            ('Прямой доступ к памяти (DMA)', 10, self._mem_topic_4()),
        ])

        # Module 5: Assembly Language
        mod5, _ = Module.objects.get_or_create(
            order_number=5,
            defaults={
                'title': 'Программирование на ассемблере',
                'description': 'Основы программирования на языке ассемблера, системы команд, директивы и макросы.',
                'icon': 'code-square',
            }
        )
        self._create_section(mod5, 1, 'Основы ассемблера', [
            ('Регистры и система команд', 15, self._asm_topic_1()),
            ('Адресация данных', 12, self._asm_topic_2()),
        ])
        self._create_section(mod5, 2, 'Разработка программ', [
            ('Структура ассемблерной программы', 12, self._asm_topic_3()),
            ('Макросы и процедуры', 10, self._asm_topic_4()),
        ])

        # Module 6: Modern Processors
        mod6, _ = Module.objects.get_or_create(
            order_number=6,
            defaults={
                'title': 'Современные микропроцессоры',
                'description': 'Многоядерные системы, суперскалярные архитектуры, энергоэффективность.',
                'icon': 'hexagon',
            }
        )
        self._create_section(mod6, 1, 'Многоядерные архитектуры', [
            ('Симметричная многопроцессорность', 12, self._modern_topic_1()),
            ('Когерентность кэша', 10, self._modern_topic_2()),
        ])
        self._create_section(mod6, 2, 'Современные технологии', [
            ('Суперскалярные процессоры', 12, self._modern_topic_3()),
            ('Энергоэффективные архитектуры', 10, self._modern_topic_4()),
        ])

        # Create test assignments for each module
        self._create_module_tests()

        # Create interactive elements (simulators) for topics
        self._create_interactive_elements()

        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена!'))

    def _create_section(self, module, order, title, topics_data):
        section, _ = Section.objects.get_or_create(
            module=module,
            order_number=order,
            defaults={'title': title, 'description': f'Раздел: {title}'},
        )
        for i, (topic_title, reading_time, content) in enumerate(topics_data, 1):
            Topic.objects.get_or_create(
                section=section,
                order_number=i,
                defaults={
                    'title': topic_title,
                    'theoretical_content': content,
                    'reading_time': reading_time,
                },
            )
        return section

    def _create_interactive_elements(self):
        """Create InteractiveElement records linking simulators to relevant topics."""

        def add_element(topic_title, sim_type, title, extra_config=None):
            topic = Topic.objects.filter(title=topic_title).first()
            if not topic:
                return
            config = {'simulator_type': sim_type}
            if extra_config:
                config.update(extra_config)
            InteractiveElement.objects.get_or_create(
                topic=topic,
                title=title,
                defaults={
                    'element_type': 'simulator',
                    'configurations': config,
                }
            )

        # Module 1 — Number System Calculator
        add_element('Что такое микропроцессор?', 'numbers', 'Калькулятор систем счисления')
        add_element('Классификация и архитектуры', 'numbers', 'Конвертер чисел (Dec/Bin/Hex)')

        # Module 2 — Cache Simulator
        add_element('Кэш-память', 'cache', 'Симулятор кэш-памяти')

        # Module 3 — Pipeline Simulator (already exists as default, but add explicitly)
        add_element('Понятие конвейера', 'pipeline', 'Визуализация 5-ступенчатого конвейера')
        add_element('5-ступенчатый конвейер RISC', 'pipeline', 'Интерактивный симулятор конвейера')

        # Module 4 — Cache + MESI
        add_element('Оперативная и постоянная память', 'cache', 'Симулятор кэш-памяти (настройка параметров)')
        add_element('Виртуальная память', 'cache', 'Конфигуратор кэша с LRU/FIFO')

        # Module 5 — RISC-V Assembler
        add_element('Регистры и система команд', 'riscv', 'RISC-V ассемблер/эмулятор')
        add_element('Адресация данных', 'riscv', 'Эмулятор RISC-V с пошаговым выполнением')
        add_element('Структура ассемблерной программы', 'riscv', 'RISC-V — примеры и выполнение кода')

        # Module 6 — MESI Protocol
        add_element('Симметричная многопроцессорность', 'mesi', 'Симулятор протокола MESI (когерентность кэша)')
        add_element('Когерентность кэша', 'mesi', 'MESI — состояние кэш-линий между ядрами')

        self.stdout.write(self.style.SUCCESS('  Созданы интерактивные элементы (симуляторы) для тем'))

    def _create_module_tests(self):
        """Create test assignments for each module."""
        modules = Module.objects.all().order_by('order_number')

        module_tests = [
            {  # Module 1 — Introduction
                'module_order': 1,
                'questions': [
                    {
                        'task_text': 'Что означает аббревиатура RISC?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 5,
                        'options': [
                            {'text': 'Reduced Instruction Set Computer'},
                            {'text': 'Random Integrated System Circuit'},
                            {'text': 'Real-time Intelligent System Controller'},
                            {'text': 'Reduced Integrated System Chip'},
                        ]
                    },
                    {
                        'task_text': 'Какой из перечисленных процессоров имеет CISC-архитектуру?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 5,
                        'options': [
                            {'text': 'Intel Core i7 (x86)'},
                            {'text': 'ARM Cortex-M4'},
                            {'text': 'RISC-V RV32I'},
                            {'text': 'MIPS R4000'},
                        ]
                    },
                    {
                        'task_text': 'В каком году был выпущен первый микропроцессор Intel 4004?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 5,
                        'options': [
                            {'text': '1971'},
                            {'text': '1965'},
                            {'text': '1980'},
                            {'text': '1975'},
                        ]
                    },
                    {
                        'task_text': 'Какое основное отличие Гарвардской архитектуры от архитектуры фон Неймана?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 10,
                        'options': [
                            {'text': 'Раздельная память для инструкций и данных'},
                            {'text': 'Использование регистров общего назначения'},
                            {'text': 'Поддержка конвейерной обработки'},
                            {'text': 'Фиксированная длина инструкции'},
                        ]
                    },
                    {
                        'task_text': 'Какая архитектура использует сокращенный набор простых команд, каждая из которых выполняется за один такт?',
                        'task_type': 'test',
                        'correct_answer': '1',
                        'max_score': 5,
                        'options': [
                            {'text': 'CISC'},
                            {'text': 'RISC'},
                            {'text': 'VLIW'},
                            {'text': 'MISD'},
                        ]
                    },
                ]
            },
            {  # Module 2 — Architecture
                'module_order': 2,
                'questions': [
                    {
                        'task_text': 'Какой регистр хранит адрес текущей выполняемой команды?',
                        'task_type': 'test',
                        'correct_answer': '1',
                        'max_score': 5,
                        'options': [
                            {'text': 'IR (Instruction Register)'},
                            {'text': 'PC (Program Counter)'},
                            {'text': 'SP (Stack Pointer)'},
                            {'text': 'PSW (Processor Status Word)'},
                        ]
                    },
                    {
                        'task_text': 'Какое устройство выполняет арифметические и логические операции?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 5,
                        'options': [
                            {'text': 'АЛУ (ALU)'},
                            {'text': 'УУ (CU)'},
                            {'text': 'Регистровый файл'},
                            {'text': 'Кэш-память L1'},
                        ]
                    },
                    {
                        'task_text': 'Какой механизм используется для ускорения трансляции виртуальных адресов в физические?',
                        'task_type': 'test',
                        'correct_answer': '2',
                        'max_score': 10,
                        'options': [
                            {'text': 'Кэш-память L2'},
                            {'text': 'Таблица страниц'},
                            {'text': 'TLB (Translation Lookaside Buffer)'},
                            {'text': 'Буфер ассоциативной трансляции'},
                        ]
                    },
                    {
                        'task_text': 'Сколько бит в регистрах общего назначения RISC-V (базовый набор RV32I)?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 5,
                        'options': [
                            {'text': '32 бита'},
                            {'text': '64 бита'},
                            {'text': '16 бит'},
                            {'text': '128 бит'},
                        ]
                    },
                    {
                        'task_text': 'Какой уровень кэша является самым быстрым по времени доступа?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 5,
                        'options': [
                            {'text': 'L1'},
                            {'text': 'L2'},
                            {'text': 'L3'},
                            {'text': 'L4'},
                        ]
                    },
                ]
            },
            {  # Module 3 — Pipeline
                'module_order': 3,
                'questions': [
                    {
                        'task_text': 'Сколько стадий содержит базовый 5-ступенчатый конвейер RISC?',
                        'task_type': 'test',
                        'correct_answer': '1',
                        'max_score': 5,
                        'options': [
                            {'text': '4'},
                            {'text': '5'},
                            {'text': '6'},
                            {'text': '7'},
                        ]
                    },
                    {
                        'task_text': 'Какой тип конфликта возникает, когда команда зависит от результата предыдущей команды?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 5,
                        'options': [
                            {'text': 'RAW (Read After Write) — истинная зависимость'},
                            {'text': 'WAR (Write After Read) — анти-зависимость'},
                            {'text': 'WAW (Write After Write) — выходная зависимость'},
                            {'text': 'Структурный конфликт'},
                        ]
                    },
                    {
                        'task_text': 'Какой метод разрешения конфликтов по данным передает результат операции напрямую между стадиями конвейера?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 10,
                        'options': [
                            {'text': 'Продвижение (Forwarding/Bypassing)'},
                            {'text': 'Вставка пузырьков (Stalling)'},
                            {'text': 'Перестановка инструкций компилятором'},
                            {'text': 'Спекулятивное выполнение'},
                        ]
                    },
                    {
                        'task_text': 'Что такое структурный конфликт в конвейере?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 10,
                        'options': [
                            {'text': 'Два этапа конвейера пытаются одновременно использовать один аппаратный ресурс'},
                            {'text': 'Команда зависит от результата предыдущей'},
                            {'text': 'Выполнение команды условного перехода'},
                            {'text': 'Неправильный порядок записи в регистры'},
                        ]
                    },
                    {
                        'task_text': 'Какая точность у современных адаптивных нейросетевых предсказателей переходов?',
                        'task_type': 'test',
                        'correct_answer': '2',
                        'max_score': 5,
                        'options': [
                            {'text': '~85%'},
                            {'text': '~90-95%'},
                            {'text': '>97%'},
                            {'text': '~75%'},
                        ]
                    },
                ]
            },
            {  # Module 4 — Memory & IO
                'module_order': 4,
                'questions': [
                    {
                        'task_text': 'Какой тип памяти используется для кэша процессора?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 5,
                        'options': [
                            {'text': 'SRAM (Static RAM)'},
                            {'text': 'DRAM (Dynamic RAM)'},
                            {'text': 'NAND Flash'},
                            {'text': 'EEPROM'},
                        ]
                    },
                    {
                        'task_text': 'Какой метод ввода-вывода требует постоянной проверки готовности устройства процессором?',
                        'task_type': 'test',
                        'correct_answer': '1',
                        'max_score': 5,
                        'options': [
                            {'text': 'Прерывательный ввод-вывод'},
                            {'text': 'Программный ввод-вывод (Polling)'},
                            {'text': 'Прямой доступ к памяти (DMA)'},
                            {'text': 'Канальный ввод-вывод'},
                        ]
                    },
                    {
                        'task_text': 'Что означает аббревиатура DMA?',
                        'task_type': 'test',
                        'correct_answer': '2',
                        'max_score': 5,
                        'options': [
                            {'text': 'Digital Memory Access'},
                            {'text': 'Direct Memory Allocation'},
                            {'text': 'Direct Memory Access'},
                            {'text': 'Dual Memory Architecture'},
                        ]
                    },
                    {
                        'task_text': 'Какой размер страницы обычно используется в страничной организации памяти?',
                        'task_type': 'test',
                        'correct_answer': '1',
                        'max_score': 5,
                        'options': [
                            {'text': '1 КБ'},
                            {'text': '4 КБ'},
                            {'text': '16 КБ'},
                            {'text': '64 КБ'},
                        ]
                    },
                ]
            },
            {  # Module 5 — Assembly
                'module_order': 5,
                'questions': [
                    {
                        'task_text': 'Какой регистр в RISC-V всегда содержит ноль?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 5,
                        'options': [
                            {'text': 'R0 (zero)'},
                            {'text': 'R1 (ra)'},
                            {'text': 'R2 (sp)'},
                            {'text': 'R10 (a0)'},
                        ]
                    },
                    {
                        'task_text': 'Какая команда RISC-V загружает слово из памяти?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 5,
                        'options': [
                            {'text': 'LW R1, 8(R2)'},
                            {'text': 'SW R1, 8(R2)'},
                            {'text': 'LI R1, 100'},
                            {'text': 'ADD R1, R2, R3'},
                        ]
                    },
                    {
                        'task_text': 'Какой режим адресации используется в инструкции LW R1, 8(R2)?',
                        'task_type': 'test',
                        'correct_answer': '2',
                        'max_score': 5,
                        'options': [
                            {'text': 'Регистровая адресация'},
                            {'text': 'Непосредственная адресация'},
                            {'text': 'Базовая адресация (Base displacement)'},
                            {'text': 'Косвенная регистровая'},
                        ]
                    },
                    {
                        'task_text': 'Для чего используется регистр SP (R2) в RISC-V?',
                        'task_type': 'test',
                        'correct_answer': '1',
                        'max_score': 5,
                        'options': [
                            {'text': 'Для возврата из функции'},
                            {'text': 'Как указатель стека'},
                            {'text': 'Как глобальный указатель'},
                            {'text': 'Для хранения временных данных'},
                        ]
                    },
                    {
                        'task_text': 'Какой регистр используется для передачи первого аргумента функции в RISC-V?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 5,
                        'options': [
                            {'text': 'R10 (a0)'},
                            {'text': 'R5 (t0)'},
                            {'text': 'R1 (ra)'},
                            {'text': 'R8 (s0)'},
                        ]
                    },
                ]
            },
            {  # Module 6 — Modern Processors
                'module_order': 6,
                'questions': [
                    {
                        'task_text': 'Что означает аббревиатура SMP?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 5,
                        'options': [
                            {'text': 'Symmetric Multiprocessing'},
                            {'text': 'Single Memory Processor'},
                            {'text': 'Shared Memory Protocol'},
                            {'text': 'System Management Processor'},
                        ]
                    },
                    {
                        'task_text': 'Какой протокол используется для обеспечения когерентности кэша?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 5,
                        'options': [
                            {'text': 'MESI (Modified, Exclusive, Shared, Invalid)'},
                            {'text': 'TCP/IP'},
                            {'text': 'PCI Express'},
                            {'text': 'USB 3.0'},
                        ]
                    },
                    {
                        'task_text': 'Что такое суперскалярный процессор?',
                        'task_type': 'test',
                        'correct_answer': '1',
                        'max_score': 10,
                        'options': [
                            {'text': 'Процессор с очень высокой тактовой частотой'},
                            {'text': 'Процессор, способный выполнять несколько инструкций за один такт'},
                            {'text': 'Процессор с пониженным энергопотреблением'},
                            {'text': 'Процессор с одним ядром и гипертредингом'},
                        ]
                    },
                    {
                        'task_text': 'Какая технология позволяет отключать тактовый сигнал неактивных блоков для экономии энергии?',
                        'task_type': 'test',
                        'correct_answer': '0',
                        'max_score': 5,
                        'options': [
                            {'text': 'Clock Gating'},
                            {'text': 'Power Gating'},
                            {'text': 'DVFS'},
                            {'text': 'Hyper-Threading'},
                        ]
                    },
                    {
                        'task_text': 'Какая архитектура сочетает производительные и энергоэффективные ядра?',
                        'task_type': 'test',
                        'correct_answer': '2',
                        'max_score': 5,
                        'options': [
                            {'text': 'UMA'},
                            {'text': 'NUMA'},
                            {'text': 'big.LITTLE'},
                            {'text': 'VLIW'},
                        ]
                    },
                ]
            },
        ]

        for test_data in module_tests:
            module = modules.filter(order_number=test_data['module_order']).first()
            if not module:
                continue

            # Get the last topic of this module to attach assignments
            last_topic = Topic.objects.filter(
                section__module=module
            ).order_by('section__order_number', 'order_number').last()

            if not last_topic:
                continue

            for q_data in test_data['questions']:
                Assignment.objects.get_or_create(
                    topic=last_topic,
                    task_text=q_data['task_text'],
                    defaults={
                        'task_type': q_data['task_type'],
                        'correct_answer': q_data['correct_answer'],
                        'max_score': q_data['max_score'],
                        'options': q_data['options'],
                    }
                )

        self.stdout.write(self.style.SUCCESS('  Созданы тестовые задания для модулей'))

    # ---- Content Generators ----
    def _intro_topic_1(self):
        return """<h2>Что такое микропроцессор?</h2>

<p>Микропроцессор (МП) — это программно-управляемое электронное цифровое устройство, предназначенное для обработки цифровой информации и управления процессом этой обработки, выполненное на одной или нескольких интегральных схемах с высокой степенью интеграции.</p>

<h3>Основные функции микропроцессора:</h3>
<ul>
    <li><strong>Арифметико-логическая обработка данных</strong> — выполнение арифметических и логических операций;</li>
    <li><strong>Управление последовательностью выполнения команд</strong> — выборка, декодирование и исполнение инструкций;</li>
    <li><strong>Управление обменом данными</strong> — взаимодействие с памятью и устройствами ввода-вывода;</li>
    <li><strong>Реакция на внешние события</strong> — обработка прерываний.</li>
</ul>

<h3>Ключевые характеристики:</h3>
<table class="table table-bordered">
    <tr><th>Характеристика</th><th>Описание</th></tr>
    <tr><td>Разрядность</td><td>Количество бит, обрабатываемых за один такт (8, 16, 32, 64 бита)</td></tr>
    <tr><td>Тактовая частота</td><td>Скорость выполнения операций (ГГц)</td></tr>
    <tr><td>Архитектура</td><td>CISC, RISC, VLIW и др.</td></tr>
    <tr><td>Объем кэш-памяти</td><td>Объем сверхбыстрой встроенной памяти</td></tr>
</table>

<h3>Примеры микропроцессоров:</h3>
<ul>
    <li>Intel Core i7/i9 — производительные процессоры для ПК и серверов</li>
    <li>ARM Cortex — энергоэффективные процессоры для мобильных устройств</li>
    <li>RISC-V — открытая архитектура с возможностью кастомизации</li>
    <li>AVR/PIC — микроконтроллеры для встраиваемых систем</li>
</ul>

<pre><code>; Простейшая программа для MIPS RISC-процессора
; Сложение двух чисел
        ADD R1, R2, R3    ; R1 = R2 + R3
        SW  R1, 0(R4)     ; Сохранить результат в память</code></pre>

<p>Микропроцессор является центральным компонентом любой вычислительной системы, определяя её производительность, энергопотребление и функциональные возможности.</p>"""

    def _intro_topic_2(self):
        return """<h2>История развития микропроцессоров</h2>

<h3>Эволюция микропроцессоров</h3>

<table class="table table-bordered">
    <tr><th>Период</th><th>Процессор</th><th>Характеристики</th></tr>
    <tr><td><strong>1971</strong></td><td>Intel 4004</td><td>4 бита, 740 кГц, 2300 транзисторов</td></tr>
    <tr><td><strong>1974</strong></td><td>Intel 8080</td><td>8 бит, 2 МГц, 6000 транзисторов</td></tr>
    <tr><td><strong>1978</strong></td><td>Intel 8086</td><td>16 бит, 5-10 МГц, 29000 транзисторов</td></tr>
    <tr><td><strong>1985</strong></td><td>Intel 80386</td><td>32 бита, 16-33 МГц, 275000 транзисторов</td></tr>
    <tr><td><strong>1993</strong></td><td>Intel Pentium</td><td>32 бит, 60-66 МГц, 3.1 млн транзисторов</td></tr>
    <tr><td><strong>2000</strong></td><td>Intel Pentium 4</td><td>32/64 бит, 1.3-3.8 ГГц, 42 млн транзисторов</td></tr>
    <tr><td><strong>2006</strong></td><td>Intel Core 2 Duo</td><td>64 бит, 1.8-3 ГГц, многоядерная архитектура</td></tr>
    <tr><td><strong>2010+</strong></td><td>Intel Core i7/i9</td><td>64 бит, 2-5+ ГГц, 6-18 ядер, миллиарды транзисторов</td></tr>
</table>

<h3>Закон Мура</h3>
<p>Гордон Мур в 1965 году предсказал, что количество транзисторов на кристалле будет удваиваться каждые 2 года. Этот закон выполнялся вплоть до начала 2020-х годов, но в настоящее время наблюдается замедление темпов роста из-за физических ограничений.</p>

<h3>Основные вехи развития:</h3>
<ul>
    <li><strong>1971</strong> — Первый микропроцессор Intel 4004</li>
    <li><strong>1981</strong> — IBM PC на базе Intel 8088</li>
    <li><strong>1995</strong> — Появление процессоров с поддержкой MMX</li>
    <li><strong>2003</strong> — 64-битные процессоры AMD64</li>
    <li><strong>2006</strong> — Переход на многоядерные архитектуры</li>
    <li><strong>2011</strong> — 3D-транзисторы (Tri-Gate)</li>
    <li><strong>2019+</strong> — Чиплетная компоновка, гетерогенные архитектуры</li>
</ul>"""

    def _intro_topic_3(self):
        return """<h2>Классификация и архитектуры микропроцессоров</h2>

<h3>CISC-архитектура (Complex Instruction Set Computer)</h3>
<p>Процессоры с полным набором сложных команд. Каждая инструкция может выполнять несколько низкоуровневых операций.</p>
<ul>
    <li><strong>Преимущества:</strong> Компактный код, богатая система команд</li>
    <li><strong>Недостатки:</strong> Сложное декодирование, высокое энергопотребление</li>
    <li><strong>Примеры:</strong> x86 (Intel, AMD)</li>
</ul>

<h3>RISC-архитектура (Reduced Instruction Set Computer)</h3>
<p>Процессоры с сокращенным набором простых команд, каждая из которых выполняется за один такт.</p>
<ul>
    <li><strong>Преимущества:</strong> Простота реализации, низкое энергопотребление, эффективный конвейер</li>
    <li><strong>Недостатки:</strong> Больший объем кода, зависимость от компилятора</li>
    <li><strong>Примеры:</strong> ARM, RISC-V, MIPS, PowerPC</li>
</ul>

<h3>Сравнение CISC и RISC</h3>
<table class="table table-bordered">
    <tr><th>Параметр</th><th>CISC</th><th>RISC</th></tr>
    <tr><td>Размер инструкции</td><td>Переменный</td><td>Фиксированный</td></tr>
    <tr><td>Тактов на инструкцию</td><td>2-15+</td><td>1</td></tr>
    <tr><td>Регистров</td><td>8-16</td><td>32-128+</td></tr>
    <tr><td>Адресация</td><td>Много режимов</td><td>Несколько простых режимов</td></tr>
    <tr><td>Декодирование</td><td>Сложное, микропрограммное</td><td>Простое, аппаратное</td></tr>
</table>

<h3>VLIW-архитектура (Very Long Instruction Word)</h3>
<p>Одна инструкция содержит несколько операций, которые выполняются параллельно. Компилятор отвечает за планирование параллелизма.</p>

<h3>Архитектура фон Неймана vs Гарвардская</h3>
<p><strong>Фон Неймана:</strong> Единое адресное пространство для кода и данных. Проще реализация, но возникает «бутылочное горлышко» при одновременном доступе.</p>
<p><strong>Гарвардская:</strong> Раздельная память для инструкций и данных. Позволяет одновременно выбирать инструкцию и операнд, что повышает производительность.</p>"""

    def _intro_topic_4(self):
        return """<h2>Встраиваемые системы</h2>

<p>Встраиваемая система (Embedded System) — специализированная вычислительная система, предназначенная для выполнения ограниченного набора задач, как правило, в составе более крупного устройства.</p>

<h3>Основные компоненты:</h3>
<ul>
    <li><strong>Микроконтроллер</strong> — CPU, память и периферия на одном кристалле</li>
    <li><strong>Память:</strong> Flash (для кода), SRAM (для данных)</li>
    <li><strong>Периферийные устройства:</strong> GPIO, UART, SPI, I2C, таймеры, АЦП/ЦАП</li>
    <li><strong>Интерфейсы связи:</strong> USB, Ethernet, CAN, Bluetooth, WiFi</li>
</ul>

<h3>Примеры микроконтроллеров:</h3>
<table class="table table-bordered">
    <tr><th>Семейство</th><th>Разрядность</th><th>Области применения</th></tr>
    <tr><td>AVR (Atmel/Microchip)</td><td>8 бит</td><td>Arduino, бытовая электроника</td></tr>
    <tr><td>PIC (Microchip)</td><td>8/16 бит</td><td>Промышленность, автомобильная электроника</td></tr>
    <tr><td>STM32 (STMicroelectronics)</td><td>32 бит (ARM Cortex-M)</td><td>Промышленность, IoT, робототехника</td></tr>
    <tr><td>ESP32 (Espressif)</td><td>32 бит</td><td>IoT, WiFi/Bluetooth устройства</td></tr>
</table>

<h3>Жизненный цикл встраиваемой системы:</h3>
<ol>
    <li>Анализ требований</li>
    <li>Выбор аппаратной платформы</li>
    <li>Разработка аппаратного обеспечения</li>
    <li>Написание встроенного ПО (C/C++, ассемблер)</li>
    <li>Отладка и тестирование</li>
    <li>Полевое обслуживание и обновления</li>
</ol>"""

    def _intro_topic_5(self):
        return """<h2>Современные тенденции развития микропроцессоров</h2>

<h3>Основные тренды:</h3>
<ul>
    <li><strong>Многоядерность:</strong> Увеличение количества ядер вместо наращивания тактовой частоты</li>
    <li><strong>Гетерогенные архитектуры:</strong> Объединение разных типов ядер (big.LITTLE)</li>
    <li><strong>Чиплетная компоновка:</strong> Сборка процессора из отдельных кристаллов (Chiplet)</li>
    <li><strong>3D-компоновка:</strong> Вертикальное интегрирование кристаллов</li>
    <li><strong>Специализированные ускорители:</strong> NPU для ИИ, GPU для графики, DSP для сигналов</li>
</ul>

<h3>Новые архитектуры:</h3>
<p><strong>RISC-V</strong> — открытая ISA, которая набирает популярность благодаря возможности свободного использования и кастомизации.</p>
<p><strong>ARMv9</strong> — новейшая архитектура ARM с улучшенной безопасностью и производительностью.</p>
<p><strong>x86-64</strong> продолжает доминировать в сегменте ПК и серверов, но сталкивается с конкуренцией со стороны ARM и RISC-V.</p>"""

    def _arch_topic_1(self):
        return """<h2>Внутренняя структура микропроцессора</h2>

<h3>Основные блоки:</h3>

<p><strong>Арифметико-логическое устройство (АЛУ/ALU)</strong> — выполняет арифметические (сложение, вычитание, умножение, деление) и логические (И, ИЛИ, НЕ, XOR) операции.</p>

<p><strong>Устройство управления (УУ/CU)</strong> — управляет последовательностью выполнения команд, декодирует инструкции и вырабатывает управляющие сигналы.</p>

<p><strong>Регистры</strong> — сверхбыстрая память внутри процессора для временного хранения данных и адресов.</p>

<h3>Основные регистры:</h3>
<table class="table table-bordered">
    <tr><th>Тип регистра</th><th>Назначение</th></tr>
    <tr><td>PC (Program Counter)</td><td>Указатель текущей команды</td></tr>
    <tr><td>IR (Instruction Register)</td><td>Хранит текущую выполняемую команду</td></tr>
    <tr><td>SP (Stack Pointer)</td><td>Указатель стека</td></tr>
    <tr><td>PSW/FLAGS</td><td>Регистр состояния/флагов</td></tr>
    <tr><td>R0-R31</td><td>Регистры общего назначения</td></tr>
</table>

<h3>Цикл выполнения команды:</h3>
<ol>
    <li><strong>IF:</strong> Выборка команды из памяти по адресу PC</li>
    <li><strong>ID:</strong> Декодирование команды и чтение операндов из регистров</li>
    <li><strong>EX:</strong> Выполнение операции в АЛУ</li>
    <li><strong>MEM:</strong> Обращение к памяти (если необходимо)</li>
    <li><strong>WB:</strong> Запись результата в регистр</li>
</ol>

<pre><code>; Цикл программы в ассемблере MIPS
; Вычисление суммы чисел от 1 до N
        ADD R0, R0, R0     ; R0 = 0 (сумма)
        ADD R1, R1, R1     ; R1 = 0 (начальное значение)
        ADDI R2, R0, 100   ; R2 = 100 (N)
loop:   ADD R0, R0, R1     ; R0 += R1
        ADDI R1, R1, 1     ; R1++
        BLT R1, R2, loop   ; if (R1 < R2) goto loop</code></pre>"""

    def _arch_topic_2(self):
        return """<h2>Система команд микропроцессора</h2>

<h3>Типы команд:</h3>

<p><strong>Команды пересылки данных:</strong></p>
<ul>
    <li><code>MOV R1, R2</code> — копирование данных между регистрами</li>
    <li><code>LW R1, addr</code> — загрузка слова из памяти</li>
    <li><code>SW R1, addr</code> — сохранение слова в память</li>
    <li><code>LDI R1, value</code> — загрузка непосредственного значения</li>
</ul>

<p><strong>Арифметические команды:</strong></p>
<ul>
    <li><code>ADD R1, R2, R3</code> — R1 = R2 + R3</li>
    <li><code>SUB R1, R2, R3</code> — R1 = R2 - R3</li>
    <li><code>MUL R1, R2, R3</code> — R1 = R2 * R3</li>
    <li><code>DIV R1, R2, R3</code> — R1 = R2 / R3</li>
</ul>

<p><strong>Логические команды:</strong></p>
<ul>
    <li><code>AND R1, R2, R3</code> — поразрядное И</li>
    <li><code>OR R1, R2, R3</code> — поразрядное ИЛИ</li>
    <li><code>XOR R1, R2, R3</code> — поразрядное исключающее ИЛИ</li>
    <li><code>NOT R1, R2</code> — инверсия</li>
</ul>

<p><strong>Команды перехода:</strong></p>
<ul>
    <li><code>BEQ R1, R2, label</code> — переход, если R1 == R2</li>
    <li><code>BNE R1, R2, label</code> — переход, если R1 != R2</li>
    <li><code>BLT R1, R2, label</code> — переход, если R1 < R2</li>
    <li><code>JMP label</code> — безусловный переход</li>
</ul>

<h3>Форматы команд RISC-V:</h3>
<p>В RISC-V все команды имеют фиксированную длину 32 бита (или 16 бит в сжатом формате):</p>
<pre><code>| 31..25 | 24..20 | 19..15 | 14..12 | 11..7 | 6..0 |
| funct7 | rs2    | rs1    | funct3 | rd    | opcode |</code></pre>"""

    def _arch_topic_3(self):
        return """<h2>Сегментная и страничная организация памяти</h2>

<h3>Сегментная организация памяти</h3>
<p>Память делится на сегменты переменного размера. Каждый сегмент имеет базовый адрес и размер. Доступ к данным осуществляется по адресу вида <code>сегмент:смещение</code>.</p>

<pre><code>; Пример адресации в реальном режиме x86
; Адрес = CS * 16 + IP
        MOV AX, 0x1000
        MOV DS, AX          ; Сегмент данных = 0x1000
        MOV BX, [0x1234]    ; Физический адрес: 0x1000 * 16 + 0x1234 = 0x11234</code></pre>

<h3>Страничная организация памяти</h3>
<p>Память делится на страницы фиксированного размера (обычно 4 КБ). Виртуальный адрес преобразуется в физический через таблицу страниц (Page Table).</p>

<h3>Преимущества страничной организации:</h3>
<ul>
    <li>Эффективное использование физической памяти</li>
    <li>Поддержка виртуальной памяти</li>
    <li>Защита памяти между процессами</li>
    <li>Подкачка (Swapping) на диск</li>
</ul>

<h3>TLB (Translation Lookaside Buffer)</h3>
<p>Специализированный кэш для ускорения трансляции виртуальных адресов в физические. Хранит недавно использованные отображения страниц.</p>"""

    def _arch_topic_4(self):
        return """<h2>Кэш-память</h2>

<p>Кэш-память — сверхбыстрая память небольшого объема, расположенная между процессором и основной памятью. Служит для ускорения доступа к часто используемым данным.</p>

<h3>Уровни кэша:</h3>
<table class="table table-bordered">
    <tr><th>Уровень</th><th>Расположение</th><th>Объем</th><th>Время доступа</th></tr>
    <tr><td>L1</td><td>Внутри ядра</td><td>16-128 КБ</td><td>1-2 такта</td></tr>
    <tr><td>L2</td><td>Внутри ядра/кристалла</td><td>256 КБ - 1 МБ</td><td>5-10 тактов</td></tr>
    <tr><td>L3</td><td>Общий для всех ядер</td><td>2-32 МБ</td><td>20-40 тактов</td></tr>
</table>

<h3>Организация кэша:</h3>
<ul>
    <li><strong>Direct-mapped:</strong> Каждый блок памяти отображается в одну конкретную строку кэша</li>
    <li><strong>Fully associative:</strong> Любой блок может быть помещен в любую строку кэша</li>
    <li><strong>N-way set-associative:</strong> Компромисс между прямым и полносвязным отображением</li>
</ul>

<h3>Политики замены:</h3>
<ul>
    <li><strong>LRU</strong> (Least Recently Used) — вытеснение давно неиспользуемых блоков</li>
    <li><strong>FIFO</strong> (First In, First Out) — вытеснение по принципу очереди</li>
    <li><strong>Random</strong> — случайное вытеснение</li>
</ul>"""

    def _pipe_topic_1(self):
        return """<h2>Понятие конвейера</h2>

<p>Конвейерная обработка — метод организации выполнения команд, при котором несколько команд находятся на разных стадиях обработки одновременно.</p>

<h3>Аналогия с конвейером производства:</h3>
<p>Представьте сборочную линию автомобильного завода. Вместо того чтобы строить один автомобиль полностью за раз, каждое рабочее место выполняет одну операцию: установка двигателя, покраска, установка колес и т.д. Если конвейер заполнен, каждую минуту с него сходит готовый автомобиль.</p>

<h3>Базовый 5-ступенчатый конвейер:</h3>
<ol>
    <li><strong>IF (Instruction Fetch)</strong> — Выборка команды из памяти</li>
    <li><strong>ID (Instruction Decode)</strong> — Декодирование команды, чтение регистров</li>
    <li><strong>EX (Execute)</strong> — Выполнение операции в АЛУ</li>
    <li><strong>MEM (Memory Access)</strong> — Доступ к памяти (чтение/запись)</li>
    <li><strong>WB (Write Back)</strong> — Запись результата в регистр</li>
</ol>

<h3>Преимущества конвейеризации:</h3>
<ul>
    <li>Увеличение пропускной способности процессора</li>
    <li>Более эффективное использование аппаратных ресурсов</li>
    <li>Потенциальный прирост производительности в <em>n</em> раз (где <em>n</em> — число ступеней)</li>
</ul>

<p>Используйте <strong>встроенный симулятор конвейера</strong> ниже для визуализации работы 5-ступенчатого конвейера!</p>"""

    def _pipe_topic_2(self):
        return """<h2>5-ступенчатый конвейер RISC</h2>

<h3>Детальное описание стадий:</h3>

<p><strong>IF (Instruction Fetch):</strong></p>
<ul>
    <li>Выборка команды из кэша L1 по адресу из PC</li>
    <li>Увеличение PC на размер команды</li>
    <li>Передача команды в конвейерный регистр IF/ID</li>
</ul>

<p><strong>ID (Instruction Decode):</strong></p>
<ul>
    <li>Декодирование команды (определение типа операции)</li>
    <li>Чтение операндов из регистров</li>
    <li>Формирование управляющих сигналов</li>
</ul>

<p><strong>EX (Execute):</strong></p>
<ul>
    <li>Выполнение арифметико-логической операции</li>
    <li>Вычисление адреса для команд обращения к памяти</li>
    <li>Проверка условия для команд условного перехода</li>
</ul>

<p><strong>MEM (Memory Access):</strong></p>
<ul>
    <li>Чтение из памяти (LW) или запись в память (SW)</li>
    <li>Доступ к кэшу данных L1</li>
</ul>

<p><strong>WB (Write Back):</strong></p>
<ul>
    <li>Запись результата в регистровый файл</li>
    <li>Завершение выполнения команды</li>
</ul>

<h3>Конвейерные регистры:</h3>
<p>Между каждой парой стадий находятся конвейерные регистры (IF/ID, ID/EX, EX/MEM, MEM/WB), которые хранят промежуточные результаты и управляющие сигналы.</p>

<pre><code>; Пример выполнения на конвейере
; ADD R1, R2, R3   ; такт 1: IF, такт 2: ID, такт 3: EX, такт 4: MEM, такт 5: WB
; ADD R4, R5, R6   ; такт 2: IF, такт 3: ID, такт 4: EX, такт 5: MEM, такт 6: WB
; ADD R7, R8, R9   ; такт 3: IF, такт 4: ID, такт 5: EX, такт 6: MEM, такт 7: WB</code></pre>"""

    def _pipe_topic_3(self):
        return """<h2>Структурные конфликты в конвейере</h2>

<p>Структурные конфликты возникают, когда два разных этапа конвейера пытаются одновременно использовать один и тот же аппаратный ресурс (память, АЛУ, шину).</p>

<h3>Пример структурного конфликта:</h3>
<p>В архитектуре с единой памятью для инструкций и данных (фон Неймана) стадия IF (выборка команды) и стадия MEM (доступ к данным) не могут выполняться одновременно.</p>

<h3>Способы разрешения:</h3>
<ul>
    <li><strong>Гарвардская архитектура:</strong> Разделение кэша инструкций и кэша данных</li>
    <li><strong>Повторение ресурсов:</strong> Установка дополнительных АЛУ, портов чтения/записи</li>
    <li><strong>Конвейерная заглушка (Pipeline Stall):</strong> Вставка пузырька (bubble) в конвейер</li>
</ul>

<pre><code>; Пример: структурный конфликт при одновременном обращении к памяти
LW    R1, 0(R2)   ; MEM стадия обращается к памяти
                    ; IF стадия не может выбрать следующую команду
                    ; => Вставляется пузырек (bubble)</code></pre>

<h3>Влияние на производительность:</h3>
<p>Структурные конфликты снижают реальную производительность конвейера ниже теоретического максимума (1 команда за такт).</p>"""

    def _pipe_topic_4(self):
        return """<h2>Конфликты по данным</h2>

<p>Конфликты по данным (Data Hazards) возникают, когда команда зависит от результата предыдущей команды, который еще не записан в регистр.</p>

<h3>Типы конфликтов по данным:</h3>

<p><strong>RAW (Read After Write) — истинная зависимость:</strong></p>
<pre><code>ADD R1, R2, R3   ; Запись в R1
SUB R4, R1, R5   ; Чтение R1 до его обновления</code></pre>

<p><strong>WAR (Write After Read) — анти-зависимость:</strong></p>
<pre><code>ADD R1, R2, R3   ; Чтение R2
SUB R2, R4, R5   ; Запись в R2</code></pre>

<p><strong>WAW (Write After Write) — выходная зависимость:</strong></p>
<pre><code>ADD R1, R2, R3   ; Запись в R1
SUB R1, R4, R5   ; Запись в R1 (неправильный порядок)</code></pre>

<h3>Методы разрешения:</h3>
<ul>
    <li><strong>Продвижение (Forwarding/Bypassing):</strong> Результат операции передается с выхода АЛУ на вход другой команды без записи в регистр</li>
    <li><strong>Вставка пузырьков (Stalling):</strong> Приостановка конвейера до готовности данных</li>
    <li><strong>Перестановка инструкций:</strong> Компилятор изменяет порядок команд для минимизации зависимостей</li>
</ul>

<h3>Продвижение данных (Operand Forwarding):</h3>
<pre><code>CLK 1: ADD R1, R2, R3   ; IF  ID  EX  MEM WB
CLK 2: SUB R4, R1, R5   ;     IF  ID  EX  MEM WB
                                          ↑
                              Продвижение результата EX → EX</code></pre>"""

    def _pipe_topic_5(self):
        return """<h2>Конфликты по управлению</h2>

<p>Конфликты по управлению (Control Hazards) возникают при выполнении команд условного и безусловного перехода. Пока не вычислен адрес перехода, конвейер не знает, какую команду выбирать следующей.</p>

<h3>Проблема:</h3>
<pre><code>BEQ R1, R2, label  ; Решение о переходе принимается на стадии EX
                    ; Пока это не произошло, IF уже выбрала следующую команду
                    ; Если переход происходит, эта команда не должна выполняться</code></pre>

<h3>Способы минимизации потерь:</h3>

<p><strong>1. Предположение перехода (Branch Prediction):</strong></p>
<ul>
    <li>Статическое: всегда предсказываем "переход не произойдет" (или наоборот)</li>
    <li>Динамическое: на основе истории предыдущих переходов (2-битный счетчик, корреляционные предсказатели)</li>
</ul>

<p><strong>2. Отложенный переход (Delayed Branch):</strong></p>
<ul>
    <li>Компилятор помещает полезную инструкцию в слот после команды перехода</li>
</ul>

<p><strong>3. Сокращение потерь:</strong></p>
<ul>
    <li>Вычисление адреса перехода на стадии ID вместо EX</li>
    <li>Добавление специальной логики для раннего определения условия</li>
</ul>

<h3>Современные предсказатели переходов:</h3>
<table class="table table-bordered">
    <tr><th>Метод</th><th>Точность</th><th>Реализация</th></tr>
    <tr><td>2-битный счетчик</td><td>~85%</td><td>Простой конечный автомат</td></tr>
    <tr><td>Корреляционные</td><td>~90-95%</td><td>Учет истории предыдущих переходов</td></tr>
    <tr><td>Адаптивные нейросетевые</td><td>>97%</td><td>Большие таблицы, нейронные сети</td></tr>
</table>"""

    def _mem_topic_1(self):
        return """<h2>Оперативная и постоянная память</h2>

<h3>Иерархия памяти:</h3>
<p>Регистры → Кэш L1 → Кэш L2 → Кэш L3 → Оперативная память (RAM) → SSD/HDD</p>

<h3>Типы оперативной памяти:</h3>
<ul>
    <li><strong>SRAM</strong> (Static RAM) — быстрая, используется для кэша, дорогая</li>
    <li><strong>DRAM</strong> (Dynamic RAM) — медленнее, дешевле, требует регенерации</li>
    <li><strong>SDRAM</strong> — синхронная DRAM</li>
    <li><strong>DDR3/DDR4/DDR5</strong> — двухскоростная SDRAM</li>
</ul>

<h3>Постоянная память:</h3>
<ul>
    <li><strong>ROM</strong> — постоянная память, программируется при изготовлении</li>
    <li><strong>PROM</strong> — программируемая ROM</li>
    <li><strong>EPROM/EEPROM</strong> — стираемая программируемая ROM</li>
    <li><strong>Flash</strong> — электрически стираемая память, основа современных SSD</li>
</ul>"""

    def _mem_topic_2(self):
        return """<h2>Виртуальная память</h2>

<p>Виртуальная память — механизм, позволяющий программам использовать адреса, отличные от физических, создавая иллюзию непрерывной памяти большего объема.</p>

<h3>Основные концепции:</h3>
<ul>
    <li><strong>Страничная организация</strong> — деление памяти на страницы (обычно 4 КБ)</li>
    <li><strong>Таблица страниц</strong> — отображение виртуальных страниц в физические</li>
    <li><strong>TLB</strong> — кэш для ускорения трансляции адресов</li>
    <li><strong>Подкачка (Swapping)</strong> — вытеснение страниц на диск</li>
</ul>

<pre><code>; Процесс трансляции адреса
; Виртуальный адрес: 0x12345678
; Индекс страницы: 0x12345 (VPN)
; Смещение: 0x678
; TLB Hit → Физический адрес: 0xA0000678
; TLB Miss → Обращение к таблице страниц в памяти</code></pre>"""

    def _mem_topic_3(self):
        return """<h2>Программный и прерывательный ввод-вывод</h2>

<h3>Программный ввод-вывод (Polling):</h3>
<p>Процессор периодически проверяет готовность устройства ввода-вывода путем опроса его регистра состояния.</p>
<pre><code>loop:   IN  R1, STATUS_PORT  ; Проверить статус устройства
        AND R2, R1, #1       ; Проверить бит готовности
        BEQ R1, R2, loop     ; Если не готов, ждать
        IN  R1, DATA_PORT     ; Прочитать данные</code></pre>

<h3>Прерывательный ввод-вывод (Interrupt-driven):</h3>
<p>Устройство инициирует передачу данных, посылая сигнал прерывания процессору.</p>

<h3>Сравнение:</h3>
<table class="table table-bordered">
    <tr><th>Параметр</th><th>Polling</th><th>Interrupt</th></tr>
    <tr><td>Загрузка CPU</td><td>Высокая (постоянная проверка)</td><td>Низкая (только при событии)</td></tr>
    <tr><td>Латентность</td><td>Низкая (постоянный опрос)</td><td>Средняя (зависит от приоритета)</td></tr>
    <tr><td>Сложность</td><td>Простая</td><td>Требуется контроллер прерываний</td></tr>
    <tr><td>Применение</td><td>Простые, быстрые устройства</td><td>Сложные, редкие события</td></tr>
</table>"""

    def _mem_topic_4(self):
        return """<h2>Прямой доступ к памяти (DMA)</h2>

<p>DMA (Direct Memory Access) — механизм, позволяющий устройствам ввода-вывода обмениваться данными с памятью напрямую, без участия процессора.</p>

<h3>Преимущества DMA:</h3>
<ul>
    <li>Освобождение процессора для других задач</li>
    <li>Высокая скорость передачи данных</li>
    <li>Эффективная работа с блоками данных</li>
</ul>

<h3>Типы DMA:</h3>
<ul>
    <li><strong>Базовый DMA</strong> — контроллер DMA управляет передачей</li>
    <li><strong>Bus Mastering</strong> — устройство само управляет шиной</li>
    <li><strong>DES (Dual Edge Sampling)</strong> — передача по обоим фронтам тактового сигнала</li>
</ul>"""

    def _asm_topic_1(self):
        return """<h2>Регистры и система команд</h2>

<h3>Система команд RISC-V (RV32I):</h3>
<p>Базовый набор содержит 47 инструкций, разделенных на категории:</p>

<h3>Регистры RISC-V:</h3>
<table class="table table-bordered">
    <tr><th>Регистр</th><th>Aлиас</th><th>Назначение</th></tr>
    <tr><td>R0</td><td>zero</td><td>Всегда ноль</td></tr>
    <tr><td>R1</td><td>ra</td><td>Адрес возврата</td></tr>
    <tr><td>R2</td><td>sp</td><td>Указатель стека</td></tr>
    <tr><td>R3-R4</td><td>gp, tp</td><td>Глобальный указатель, нить</td></tr>
    <tr><td>R5-R7</td><td>t0-t2</td><td>Временные регистры</td></tr>
    <tr><td>R8-R9</td><td>s0-s1</td><td>Сохраненные регистры</td></tr>
    <tr><td>R10-R17</td><td>a0-a7</td><td>Аргументы/возврат</td></tr>
    <tr><td>R18-R27</td><td>s2-s11</td><td>Сохраненные регистры</td></tr>
    <tr><td>R28-R31</td><td>t3-t6</td><td>Временные регистры</td></tr>
</table>

<pre><code>; Пример программы RISC-V
.global main
main:
    addi  sp, sp, -16    ; Выделить место в стеке
    sw    ra, 12(sp)     ; Сохранить адрес возврата
    li    a0, 42         ; Загрузить аргумент
    jal   print_int      ; Вызов функции
    lw    ra, 12(sp)     ; Восстановить адрес возврата
    addi  sp, sp, 16     ; Восстановить стек
    ret                  ; Возврат из функции</code></pre>"""

    def _asm_topic_2(self):
        return """<h2>Адресация данных</h2>

<h3>Режимы адресации:</h3>
<p><strong>Регистровая адресация:</strong></p>
<pre><code>ADD R1, R2, R3    ; Операнды находятся в регистрах</code></pre>

<p><strong>Непосредственная адресация (Immediate):</strong></p>
<pre><code>ADDI R1, R2, 100   ; R1 = R2 + 100</code></pre>

<p><strong>Базовая адресация (Base displacement):</strong></p>
<pre><code>LW R1, 8(R2)       ; R1 = Memory[R2 + 8]</code></pre>

<p><strong>Косвенная регистровая:</strong></p>
<pre><code>LW R1, (R2)        ; R1 = Memory[R2]</code></pre>

<p><strong>Относительная адресация (PC-relative):</strong></p>
<pre><code>BEQ R1, R2, label   ; PC = PC + offset (если R1 == R2)</code></pre>"""

    def _asm_topic_3(self):
        return """<h2>Структура ассемблерной программы</h2>

<pre><code>; Полная программа на RISC-V (RARS Simulator)
; Вычисление факториала числа N

.data                        ; Секция данных
    N:      .word   5        ; Исходное число
    result: .word   0        ; Место для результата
    msg:    .asciz  "Factorial: "

.text                        ; Секция кода
.global main
main:
    la      a0, msg
    jal     print_string      ; Вывести сообщение
    
    la      t0, N
    lw      a0, 0(t0)         ; Загрузить N
    jal     factorial         ; Вычислить факториал
    
    la      t0, result
    sw      a0, 0(t0)         ; Сохранить результат
    
    jal     print_int         ; Вывести результат
    li      a7, 10            ; Системный вызов: выход
    ecall

factorial:
    addi    sp, sp, -8
    sw      ra, 4(sp)
    sw      a0, 0(sp)
    
    li      t0, 1
    ble     a0, t0, base_case  ; Если N <= 1
    
    addi    a0, a0, -1
    jal     factorial           ; Рекурсивный вызов
    lw      t1, 0(sp)           ; Восстановить N
    mul     a0, a0, t1          ; N * factorial(N-1)
    j       return

base_case:
    li      a0, 1               ; factorial(0) = factorial(1) = 1

return:
    lw      ra, 4(sp)
    addi    sp, sp, 8
    jr      ra</code></pre>"""

    def _asm_topic_4(self):
        return """<h2>Макросы и процедуры</h2>

<h3>Макросы в ассемблере:</h3>
<p>Макрос — это шаблон кода, который подставляется в текст программы на этапе ассемблирования.</p>

<pre><code>; Определение макроса
.macro  swap   %reg1, %reg2
    xor %reg1, %reg1, %reg2
    xor %reg2, %reg1, %reg2
    xor %reg1, %reg1, %reg2
.end_macro

; Использование макроса
    swap t0, t1   ; Обменять значения t0 и t1</code></pre>

<h3>Процедуры (функции):</h3>
<p>Процедуры в ассемблере следуют соглашению о вызовах (Calling Convention):</p>
<ul>
    <li>Аргументы передаются через регистры a0-a7</li>
    <li>Результат возвращается через a0</li>
    <li>Сохраненные регистры (s0-s11) должны быть восстановлены</li>
    <li>Стек используется для временного хранения</li>
</ul>

<pre><code>; Пример использования стека в процедуре
push:
    addi    sp, sp, -8    ; Выделить 8 байт в стеке
    sw      ra, 4(sp)     ; Сохранить адрес возврата
    sw      s0, 0(sp)     ; Сохранить s0
    ; ... тело процедуры ...
    lw      s0, 0(sp)     ; Восстановить s0
    lw      ra, 4(sp)     ; Восстановить ra
    addi    sp, sp, 8     ; Восстановить стек
    ret</code></pre>"""

    def _modern_topic_1(self):
        return """<h2>Симметричная многопроцессорность (SMP)</h2>

<p>SMP — архитектура, в которой два или более одинаковых процессора подключены к общей памяти через общую шину или коммутатор.</p>

<h3>Архитектуры многопроцессорных систем:</h3>
<ul>
    <li><strong>UMA</strong> (Uniform Memory Access) — равный доступ к памяти для всех процессоров</li>
    <li><strong>NUMA</strong> (Non-Uniform Memory Access) — разное время доступа к разным областям памяти</li>
    <li><strong>COMA</strong> (Cache-Only Memory Architecture) — только кэш-память без основной</li>
</ul>

<h3>Проблемы SMP:</h3>
<ul>
    <li>Когерентность кэша</li>
    <li>Синхронизация доступа к разделяемым данным</li>
    <li>Узкое место шины памяти</li>
    <li>Планирование процессов</li>
</ul>"""

    def _modern_topic_2(self):
        return """<h2>Когерентность кэша</h2>

<p>В многопроцессорных системах каждый процессор имеет свой кэш. При модификации данных одним процессором, копии данных в кэшах других процессоров становятся неактуальными.</p>

<h3>Протоколы когерентности:</h3>
<p><strong>MESI (Modified, Exclusive, Shared, Invalid):</strong></p>
<ul>
    <li><strong>M</strong> (Modified) — строка модифицирована, только в этом кэше</li>
    <li><strong>E</strong> (Exclusive) — строка не модифицирована, только в этом кэше</li>
    <li><strong>S</strong> (Shared) — строка не модифицирована, есть в нескольких кэшах</li>
    <li><strong>I</strong> (Invalid) — строка невалидна</li>
</ul>

<h3>Протокол MOESI:</h3>
<p>Расширение MESI с состоянием <strong>O</strong> (Owned) для оптимизации.</p>"""

    def _modern_topic_3(self):
        return """<h2>Суперскалярные процессоры</h2>

<p>Суперскалярные процессоры способны выполнять несколько инструкций за один такт за счет параллельной работы нескольких исполнительных устройств.</p>

<h3>Ключевые концепции:</h3>
<ul>
    <li><strong>Множественные конвейеры</strong> — несколько параллельных конвейеров</li>
    <li><strong>Динамическое планирование</strong> — изменение порядка выполнения инструкций</li>
    <li><strong>Спекулятивное выполнение</strong> — выполнение инструкций до подтверждения перехода</li>
    <li><strong>Out-of-Order (OoO)</strong> — выполнение инструкций вне программного порядка</li>
</ul>

<h3>Примеры суперскалярных процессоров:</h3>
<ul>
    <li>Intel Core i9-13900K — 8 P-ядер + 16 E-ядер</li>
    <li>AMD Ryzen 9 7950X — 16 ядер, 32 потока</li>
    <li>Apple M2 Ultra — до 24 ядер CPU, 76 ядер GPU</li>
</ul>"""

    def _modern_topic_4(self):
        return """<h2>Энергоэффективные архитектуры</h2>

<h3>Техники энергосбережения:</h3>
<ul>
    <li><strong>Dynamic Voltage and Frequency Scaling (DVFS)</strong> — динамическое изменение напряжения и частоты</li>
    <li><strong>Clock Gating</strong> — отключение тактового сигнала неактивных блоков</li>
    <li><strong>Power Gating</strong> — полное отключение питания неактивных блоков</li>
    <li><strong>Гетерогенные архитектуры</strong> — сочетание производительных и энергоэффективных ядер</li>
</ul>

<h3>Гетерогенные вычисления:</h3>
<p>Архитектура ARM big.LITTLE: производительные ядра (Cortex-A7x) для сложных задач и энергоэффективные ядра (Cortex-A5x) для фоновых операций.</p>

<h3>Сравнение производительных и энергоэффективных ядер:</h3>
<table class="table table-bordered">
    <tr><th>Параметр</th><th>P-core (Performance)</th><th>E-core (Efficiency)</th></tr>
    <tr><td>Тактовая частота</td><td>До 5+ ГГц</td><td>До 3 ГГц</td></tr>
    <tr><td>Энергопотребление</td><td>15-100 Вт</td><td>1-3 Вт</td></tr>
    <tr><td>Потоков на ядро</td><td>2 (Hyper-Threading)</td><td>1</td></tr>
    <tr><td>Размер кэша L2</td><td>2-4 МБ</td><td>512 КБ - 2 МБ</td></tr>
</table>"""
