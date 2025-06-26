// Compiler UI Controller
class CompilerVisualizer {
  constructor() {
    this.animationSpeed = 600; // ms between phases
    this.initElements();
    this.setupEventListeners();
    this.initState();
  }

  initElements() {
    // Phase visualization elements
    this.phases = {
      lexical: document.getElementById('phase-lexical'),
      syntax: document.getElementById('phase-syntax'),
      semantic: document.getElementById('phase-semantic'),
      intermediate: document.getElementById('phase-intermediate'),
      optimization: document.getElementById('phase-optimization'),
      codegen: document.getElementById('phase-codegen')
    };

    // Tab system elements
    this.tabButtons = document.querySelectorAll('.tab-btn');
    this.tabContents = document.querySelectorAll('.tab-content');
    
    // Language selector
    this.langButtons = document.querySelectorAll('.lang-btn');
    this.langInput = document.getElementById('language-input');
    
    // Form and editor
    this.compileForm = document.querySelector('form');
    this.codeEditor = document.querySelector('.code-editor');
  }

  initState() {
    // Set initial active tab from template
    const initialTab = document.querySelector('.tab-btn.active')?.dataset.tab || 'output';
    this.switchTab(initialTab);
    
    // Set initial language
    const initialLang = document.querySelector('.lang-btn.active')?.dataset.lang || 'python';
    this.updateEditorLanguage(initialLang);
  }

  setupEventListeners() {
    // Tab switching
    this.tabButtons.forEach(btn => {
      btn.addEventListener('click', () => this.switchTab(btn.dataset.tab));
    });

    // Language selection
    this.langButtons.forEach(btn => {
      btn.addEventListener('click', () => this.handleLanguageChange(btn));
    });

    // Form submission
    this.compileForm?.addEventListener('submit', () => {
      this.handleCompilationStart();
    });
  }

  switchTab(tabId) {
    // Update active tab button
    this.tabButtons.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === tabId);
    });

    // Show corresponding content
    this.tabContents.forEach(content => {
      if (content.id === `${tabId}-tab`) {
        content.style.display = 'block';
        // Trigger custom event for tab change
        document.dispatchEvent(new CustomEvent('tabChanged', { detail: tabId }));
      } else {
        content.style.display = 'none';
      }
    });
  }

  handleLanguageChange(button) {
    this.langButtons.forEach(b => b.classList.remove('active'));
    button.classList.add('active');
    const lang = button.dataset.lang;
    this.langInput.value = lang;
    this.updateEditorLanguage(lang);
    
    // Dispatch event for language change
    document.dispatchEvent(new CustomEvent('languageChanged', { detail: lang }));
  }

  updateEditorLanguage(lang) {
    this.codeEditor.classList.remove('language-python', 'language-javascript');
    this.codeEditor.classList.add(`language-${lang}`);
  }

  handleCompilationStart() {
    this.resetPhaseVisualization();
    setTimeout(() => this.visualizeCompilation(), 100);
  }

  resetPhaseVisualization() {
    Object.values(this.phases).forEach(phase => {
      phase.classList.remove('active', 'error', 'warning');
    });
  }

  visualizeCompilation() {
    const phaseElements = [
      'lexical', 'syntax', 'semantic', 
      'intermediate', 'optimization', 'codegen'
    ];

    phaseElements.forEach((phase, index) => {
      setTimeout(() => {
        const phaseElement = this.phases[phase];
        if (!phaseElement) return;

        // Check phase status from data attribute
        const status = phaseElement.dataset.status;
        
        if (status === 'success') {
          phaseElement.classList.add('active');
          this.updatePhaseContent(phase);
        } else if (status === 'error') {
          phaseElement.classList.add('error');
        } else {
          phaseElement.classList.add('warning');
        }
      }, index * this.animationSpeed);
    });
  }

  updatePhaseContent(phaseName) {
    // Could be extended to show phase-specific details
    console.log(`Updating content for ${phaseName} phase`);
  }
}

// Initialize when DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
  window.compilerUI = new CompilerVisualizer();
});