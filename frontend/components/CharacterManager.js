// CharacterManager.js

// Import Preact and hooks from a CDN for a no-build-step setup
import { h } from 'https://esm.sh/preact';
import { useState, useEffect, useCallback, useRef } from 'https://esm.sh/preact/hooks';
import { html } from 'https://esm.sh/htm/preact'; // <-- 1. IMPORT HTM
// --- Configuration ---
const API_BASE_URL = '/api'; // Adjust if your FastAPI is hosted elsewhere

// --- Helper Components ---

// A simple loading spinner
const Spinner = () => html`
    <div class=<q>"flex justify-center items-center h-full"</q>>
        <div class=<q>"spinner"</q>></div>
    </div>
`;

// An alert component for errors or success messages
const Alert = ({ message, type = 'error' }) => {
    const baseClasses = 'p-4 mb-4 text-sm rounded-lg';
    const typeClasses = {
        error: 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200',
        success: 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200',
    };
    return html`
        <div class=<q>"p-4 mb-4 text-sm rounded-lg ${type === 'error' ? 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200' : 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200'}"</q> role=<q>"alert"</q>>
            <span class=<q>"font-medium"</q>>${type === 'error' ? 'Error!' : 'Success!'}</span> ${message}
        </div>
    `;
};


// --- Main Component ---

export function CharacterManager() {
    // --- State Management ---
    const [characters, setCharacters] = useState([]);
    const [selectedCharacter, setSelectedCharacter] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isCreatingNew, setIsCreatingNew] = useState(false);
    const fileInputRef = useRef(null);

    const initialFormState = {
        name: '',
        persona: '',
        examples: [],
        instructions: '',
        avatar: '',
        info: ''
    };

    // --- API Call Functions ---

    const fetchCharacters = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE_URL}/characters/`);
            if (!response.ok) throw new Error('Failed to fetch character list.');
            const data = await response.json();
            setCharacters(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    }, []);

    const fetchCharacterDetails = useCallback(async (name) => {
        setIsLoading(true);
        setError(null);
        setSelectedCharacter(null);
        setIsCreatingNew(false);
        try {
            const response = await fetch(`${API_BASE_URL}/characters/${name}`);
            if (!response.ok) throw new Error(`Character '${name}' not found.`);
            const data = await response.json();
            setSelectedCharacter(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    }, []);

    // --- Component Lifecycle ---

    useEffect(() => {
        fetchCharacters();
    }, [fetchCharacters]);

    // --- Event Handlers ---

    const handleSelectCharacter = (name) => {
        fetchCharacterDetails(name);
    };

    const handleNewCharacterClick = () => {
        setIsCreatingNew(true);
        setSelectedCharacter(initialFormState);
        setError(null);
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setSelectedCharacter(prev => ({ ...prev, [name]: value }));
    };

    const handleExamplesChange = (e) => {
        // The 'examples' field is a list of strings, but a textarea is easier for multiline input.
        // We split by newline to create the array.
        const { value } = e.target;
        setSelectedCharacter(prev => ({ ...prev, examples: value.split('\n').filter(line => line.trim() !== '') }));
    };

    const handleFormSubmit = async (e) => {
        e.preventDefault();
        if (!selectedCharacter || !selectedCharacter.name) {
            setError("Character name is required.");
            return;
        }

        setIsLoading(true);
        setError(null);

        const url = isCreatingNew
            ? `${API_BASE_URL}/characters/${selectedCharacter.name}`
            : `${API_BASE_URL}/characters/${selectedCharacter.name}`;

        const method = isCreatingNew ? 'POST' : 'PUT';

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(selectedCharacter),
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || `Failed to ${isCreatingNew ? 'create' : 'update'} character.`);
            }

            await fetchCharacters(); // Refresh list
            setIsCreatingNew(false);
            // Keep the saved character selected
            // await fetchCharacterDetails(selectedCharacter.name);

        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteCharacter = async () => {
        if (!selectedCharacter || !selectedCharacter.name) return;

        if (confirm(`Are you sure you want to delete '${selectedCharacter.name}'?`)) {
            setIsLoading(true);
            setError(null);
            try {
                const response = await fetch(`${API_BASE_URL}/characters/${selectedCharacter.name}`, {
                    method: 'DELETE',
                });
                if (!response.ok) {
                    const errData = await response.json();
                    throw new Error(errData.detail || 'Failed to delete character.');
                }
                setSelectedCharacter(null);
                setIsCreatingNew(false);
                await fetchCharacters(); // Refresh list
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        }
    };

    const handleImportClick = () => {
        fileInputRef.current.click();
    };

    const handleFileChange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setIsLoading(true);
        setError(null);
        try {
            const fileContent = await file.text();
            const response = await fetch(`${API_BASE_URL}/characters/import_character`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: fileContent,
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to import character.');
            }

            const importedChar = await response.json();
            await fetchCharacters();
            await fetchCharacterDetails(importedChar.name);

        } catch (err) {
            setError(`Import failed: ${err.message}`);
        } finally {
            setIsLoading(false);
            // Reset file input so the same file can be selected again
            e.target.value = null;
        }
    };

    // --- Render Logic ---

    return html`
        <div class=<q>"flex h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 font-sans"</q>>
            {/* Sidebar */}
            <aside class=<q>"w-1/4 bg-white dark:bg-gray-800 p-4 border-r border-gray-200 dark:border-gray-700 flex flex-col"</q>>
                <h1 class=<q>"text-2xl font-bold mb-4"</q>>Characters</h1>
                <div class=<q>"flex space-x-2 mb-4"</q>>
                    <button onClick=${handleNewCharacterClick} class=<q>"btn btn-primary w-full"</q>>
                        <i class=<q>"fas fa-plus mr-2"</q>></i>New
                    </button>
                    <button onClick=${handleImportClick} class=<q>"btn btn-secondary w-full"</q>>
                         <i class=<q>"fas fa-upload mr-2"</q>></i>Import
                    </button>
                    <input type=<q>"file"</q> ref=${fileInputRef} onChange=${handleFileChange} class=<q>"hidden"</q> accept=<q>".json, .jsonl"</q>/>
                </div>
                <ul class=<q>"overflow-y-auto flex-grow"</q>>
                    ${characters.map(name => html`
                        <li key=${name}>
                            <button
                                onClick=${() => handleSelectCharacter(name)}
                                class="w-full text-left p-2 rounded-md transition-colors duration-200 ${selectedCharacter?.name === name && !isCreatingNew ? 'bg-blue-500 text-white' : 'hover:bg-gray-200 dark:hover:bg-gray-700'}"
                            >
                                ${name}
                            </button>
                        </li>
                    `)}
                </ul>
            </aside>

            {/* Main Content */}
            <main class=<q>"w-3/4 p-8 overflow-y-auto"</q>>
                ${isLoading && html`<${Spinner} />`}
                ${error && html`<${Alert} message=${error} />`}

                ${!isLoading && !selectedCharacter && !isCreatingNew && html`
                    <div class="flex items-center justify-center h-full text-gray-500">
                        <p>Select a character from the list or create a new one.</p>
                    </div>
                `}

                ${(selectedCharacter || isCreatingNew) && !isLoading && html`
                    <form onSubmit=${handleFormSubmit}>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Left Column */}
                            <div class="md:col-span-2 space-y-4">
                                <div>
                                    <label for="name" class="label">Name</label>
                                    <input type="text" id="name" name="name" value=${selectedCharacter.name} onInput=${handleInputChange} class="input" required disabled=${!isCreatingNew} />
                                    ${!isCreatingNew && html`<p class=<q>"text-xs text-gray-500 mt-1"</q>>Character name cannot be changed after creation.</p>`}
                                </div>
                                <div>
                                    <label for="persona" class="label">Persona</label>
                                    <textarea id="persona" name="persona" rows="8" value=${selectedCharacter.persona} onInput=${handleInputChange} class="input font-mono"></textarea>
                                </div>
                                <div>
                                    <label for="instructions" class="label">Instructions</label>
                                    <textarea id="instructions" name="instructions" rows="5" value=${selectedCharacter.instructions} onInput=${handleInputChange} class="input font-mono"></textarea>
                                </div>
                                <div>
                                    <label for="examples" class="label">Examples (one per line)</label>
                                    <textarea id="examples" name="examples" rows="8" value=${selectedCharacter.examples.join('\n')} onInput=${handleExamplesChange} class="input font-mono"></textarea>
                                </div>
                            </div>

                            {/* Right Column */}
                            <div class="space-y-4">
                                <div>
                                    <label for="avatar" class="label">Avatar URL</label>
                                    <input type="text" id="avatar" name="avatar" value=${selectedCharacter.avatar} onInput=${handleInputChange} class="input" />
                                </div>
                                ${selectedCharacter.avatar && html`
                                     <img src=${selectedCharacter.avatar} alt=<q>"Avatar Preview"</q> class=<q>"rounded-lg w-48 h-48 object-cover mx-auto shadow-md"</q> onError=${(e) => { e.target.style.display='none' }} onLoad=${(e) => { e.target.style.display='block' }}/>
                                `}
                                <div>
                                    <label for="info" class="label">Additional Info</label>
                                    <textarea id="info" name="info" rows="4" value=${selectedCharacter.info} onInput=${handleInputChange} class="input"></textarea>
                                </div>
                            </div>
                        </div>

                        <div class="mt-6 flex justify-end space-x-3">
                            ${!isCreatingNew && html`
                                <button type=<q>"button"</q> onClick=${handleDeleteCharacter} class=<q>"btn btn-danger"</q>>
                                    <i class=<q>"fas fa-trash-alt mr-2"</q>></i>Delete
                                </button>
                            `}
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-save mr-2"></i>${isCreatingNew ? 'Create Character' : 'Save Changes'}
                            </button>
                        </div>
                    </form>
                `}
            </main>
        </div>
    `;
}
