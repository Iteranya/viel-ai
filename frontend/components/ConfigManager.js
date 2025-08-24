// ConfigManager.js

// Import Preact and hooks from a CDN
import { h } from 'https://esm.sh/preact';
import { useState, useEffect, useCallback } from 'https://esm.sh/preact/hooks';
import { html } from 'https://esm.sh/htm/preact'; // <-- 1. IMPORT HTM
// --- Configuration ---
const API_BASE_URL = '/api'; // Adjust if your FastAPI is hosted elsewhere

// --- Helper Components (These can be shared across your app) ---

const Spinner = () => html`
    <div class="flex justify-center items-center my-4">
        <div class="spinner"></div>
    </div>
`;

const Alert = ({ message, type = 'error', onDismiss }) => {
    const baseClasses = 'p-4 mb-4 text-sm rounded-lg flex justify-between items-center';
    const typeClasses = {
        error: 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200',
        success: 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200',
    };

    return html`
        <div class="${baseClasses} ${typeClasses[type]}" role="alert">
            <div>
                <span class="font-medium">${type === 'error' ? 'Error!' : 'Success!'}</span> ${message}
            </div>
            ${onDismiss && html`
                <button onClick=${onDismiss} class="ml-4 -mr-1 p-1 rounded-md hover:bg-opacity-20 hover:bg-current">
                    <i class="fas fa-times"></i>
                </button>
            `}
        </div>
    `;
};

// --- Main Component ---

export function ConfigManager() {
    // --- State Management ---
    const initialConfig = {
        default_character: 'Viel',
        ai_endpoint: '',
        base_llm: '',
        temperature: 0.5,
        auto_cap: 0,
        ai_key: '',
        discord_key: '',
    };

    const [config, setConfig] = useState(initialConfig);
    const [characters, setCharacters] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);
    const [showKeys, setShowKeys] = useState(false);

    // --- API Call Functions ---

    const fetchConfig = useCallback(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/config/`);
            if (!response.ok) throw new Error('Failed to fetch configuration.');
            const data = await response.json();
            setConfig(data);
        } catch (err) {
            setError(err.message);
        }
    }, []);

    const fetchCharacters = useCallback(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/characters/`);
            if (!response.ok) throw new Error('Failed to fetch character list.');
            const data = await response.json();
            setCharacters(data);
        } catch (err) {
            // Non-critical error, just log it or show a small warning
            console.error("Could not load character list:", err.message);
        }
    }, []);

    // --- Component Lifecycle ---

    useEffect(() => {
        const loadData = async () => {
            setIsLoading(true);
            setError(null);
            await Promise.all([fetchConfig(), fetchCharacters()]);
            setIsLoading(false);
        };
        loadData();
    }, [fetchConfig, fetchCharacters]);

    // --- Event Handlers ---

    const handleInputChange = (e) => {
        const { name, value, type } = e.target;
        const val = type === 'number' ? parseFloat(value) : value;
        setConfig(prev => ({ ...prev, [name]: val }));
    };

    const handleFormSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        setSuccessMessage(null);

        try {
            const response = await fetch(`${API_BASE_URL}/config/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config),
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to save configuration.');
            }

            const savedConfig = await response.json();
            setConfig(savedConfig); // Update state with potentially preserved keys
            setSuccessMessage('Configuration saved successfully!');
            setTimeout(() => setSuccessMessage(null), 3000); // Hide after 3 seconds

        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    // --- Render Logic ---

    if (isLoading && !config.base_llm) {
        return html`<${Spinner} />`;
    }

    return html`
        <div class="max-w-4xl mx-auto p-8 bg-white dark:bg-gray-800 rounded-lg shadow-md text-gray-900 dark:text-gray-100 font-sans">
            <h1 class="text-3xl font-bold mb-6 border-b border-gray-300 dark:border-gray-600 pb-4">Bot Configuration</h1>

            ${error && html`<${Alert} message=${error} onDismiss=${() => setError(null)} />`}
            ${successMessage && html`<${Alert} message=${successMessage} type="success" onDismiss=${() => setSuccessMessage(null)} />`}

            <form onSubmit=${handleFormSubmit}>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Left Column */}
                    <div class="space-y-6">
                        <div>
                            <label for="default_character" class="label">Default Character</label>
                            <select id="default_character" name="default_character" value=${config.default_character} onChange=${handleInputChange} class="input">
                                ${characters.map(char => html`<option key=${char} value=${char}>${char}</option>`)}
                                ${!characters.includes(config.default_character) && html`<option value=${config.default_character} disabled>${config.default_character} (current)</option>`}
                            </select>
                        </div>
                        <div>
                            <label for="ai_endpoint" class="label">AI Endpoint</label>
                            <input type="text" id="ai_endpoint" name="ai_endpoint" value=${config.ai_endpoint} onInput=${handleInputChange} class="input font-mono" required />
                        </div>
                        <div>
                            <label for="base_llm" class="label">Base LLM</label>
                            <input type="text" id="base_llm" name="base_llm" value=${config.base_llm} onInput=${handleInputChange} class="input font-mono" required />
                        </div>
                    </div>

                    {/* Right Column */}
                    <div class="space-y-6">
                        <div>
                            <label for="temperature" class="label flex justify-between">
                                <span>Temperature</span>
                                <span class="font-mono bg-gray-200 dark:bg-gray-700 px-2 py-0.5 rounded">${config.temperature.toFixed(2)}</span>
                            </label>
                            <input type="range" id="temperature" name="temperature" min="0" max="2" step="0.05" value=${config.temperature} onInput=${handleInputChange} class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700" />
                        </div>
                        <div>
                            <label for="auto_cap" class="label">Auto-Reply Cap</label>
                            <input type="number" id="auto_cap" name="auto_cap" min="0" step="1" value=${config.auto_cap} onInput=${handleInputChange} class="input" />
                             <p class="text-xs text-gray-500 mt-1">How many times the bot can auto-reply. 0 disables.</p>
                        </div>
                        <div>
                            <label for="ai_key" class="label">AI API Key</label>
                            <div class="relative">
                                <input type=${showKeys ? 'text' : 'password'} id="ai_key" name="ai_key" value=${config.ai_key} onInput=${handleInputChange} class="input pr-10" />
                                <button type="button" onClick=${() => setShowKeys(!showKeys)} class="absolute inset-y-0 right-0 px-3 text-gray-500">
                                    <i class="fas ${showKeys ? 'fa-eye-slash' : 'fa-eye'}"></i>
                                </button>
                            </div>
                            <p class="text-xs text-gray-500 mt-1">Leave blank to keep the current key.</p>
                        </div>
                         <div>
                            <label for="discord_key" class="label">Discord Key</label>
                            <div class="relative">
                                <input type=${showKeys ? 'text' : 'password'} id="discord_key" name="discord_key" value=${config.discord_key} onInput=${handleInputChange} class="input pr-10" />
                                <button type="button" onClick=${() => setShowKeys(!showKeys)} class="absolute inset-y-0 right-0 px-3 text-gray-500">
                                    <i class="fas ${showKeys ? 'fa-eye-slash' : 'fa-eye'}"></i>
                                </button>
                            </div>
                            <p class="text-xs text-gray-500 mt-1">Leave blank to keep the current key.</p>
                        </div>
                    </div>
                </div>

                <div class="mt-8 pt-6 border-t border-gray-300 dark:border-gray-600 flex justify-end">
                    <button type="submit" class="btn btn-success w-full md:w-auto" disabled=${isLoading}>
                        ${isLoading ? html`<span class="spinner-sm"></span>` : html`<i class="fas fa-save mr-2"></i>Save Changes`}
                    </button>
                </div>
            </form>
        </div>
    `;
}
