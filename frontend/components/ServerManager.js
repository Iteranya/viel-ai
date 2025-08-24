// ServerManager.js

// Import Preact and hooks from a CDN
import { h } from 'https://esm.sh/preact';
import { useState, useEffect, useCallback } from 'https://esm.sh/preact/hooks';

// --- Configuration ---
const API_BASE_URL = '/api'; // Adjust if your FastAPI is hosted elsewhere

// --- Helper Components (Can be shared with CharacterManager) ---

const Spinner = () => html`
    <div class=<q>"flex justify-center items-center h-full"</q>>
        <div class=<q>"spinner"</q>></div>
    </div>
`;

const Alert = ({ message, type = 'error', onDismiss }) => {
    return html`
        <div class="p-4 mb-4 text-sm rounded-lg flex justify-between items-center ${type === 'error' ? 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200' : 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200'}" role="alert">
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

export function ServerManager() {
    // --- State Management ---
    const [servers, setServers] = useState([]);
    const [channels, setChannels] = useState([]);
    const [selectedServer, setSelectedServer] = useState(null);
    const [selectedChannel, setSelectedChannel] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isCreatingNew, setIsCreatingNew] = useState(false);
    const [lorebookError, setLorebookError] = useState(null);

    const initialFormState = {
        name: '',
        instruction: '',
        globalvar: '',
        location: '',
        lorebook: {},
        whitelist: [],
    };

    // --- API Call Functions ---

    const fetchServers = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE_URL}/servers/`);
            if (!response.ok) throw new Error('Failed to fetch server list.');
            const data = await response.json();
            setServers(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    }, []);

    const fetchChannels = useCallback(async (serverName) => {
        setIsLoading(true);
        setError(null);
        setChannels([]); // Clear previous channels
        try {
            const response = await fetch(`${API_BASE_URL}/servers/${serverName}/channels`);
            if (!response.ok) throw new Error(`Failed to fetch channels for server '${serverName}'.`);
            const data = await response.json();
            setChannels(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    }, []);

    const fetchChannelDetails = useCallback(async (serverName, channelName) => {
        setIsLoading(true);
        setError(null);
        setSelectedChannel(null);
        setIsCreatingNew(false);
        try {
            const response = await fetch(`${API_BASE_URL}/servers/${serverName}/channels/${channelName}`);
            if (!response.ok) throw new Error(`Channel '${channelName}' not found.`);
            const data = await response.json();
            setSelectedChannel(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    }, []);

    // --- Component Lifecycle ---

    useEffect(() => {
        fetchServers();
    }, [fetchServers]);

    // --- Event Handlers ---

    const handleSelectServer = (serverName) => {
        setSelectedServer(serverName);
        setSelectedChannel(null);
        setIsCreatingNew(false);
        fetchChannels(serverName);
    };

    const handleNewServerClick = () => {
        const serverName = prompt("Enter new server name:");
        if (serverName && !servers.includes(serverName)) {
            // Your API creates servers implicitly when a channel is created.
            // So we just add it to the UI list and select it.
            setServers(prev => [...prev, serverName].sort());
            handleSelectServer(serverName);
        } else if (servers.includes(serverName)) {
            alert(`Server '${serverName}' already exists.`);
        }
    };

    const handleNewChannelClick = () => {
        if (!selectedServer) {
            alert("Please select a server first.");
            return;
        }
        setIsCreatingNew(true);
        setSelectedChannel(initialFormState);
        setError(null);
    };

    const handleSelectChannel = (channelName) => {
        if (selectedServer) {
            fetchChannelDetails(selectedServer, channelName);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setSelectedChannel(prev => ({ ...prev, [name]: value }));
    };


    const handleListChange = (e) => { // For whitelist
        const { value } = e.target;
        setSelectedChannel(prev => ({ ...prev, whitelist: value.split('\n').filter(line => line.trim() !== '') }));
    };

    const handleLorebookChange = (e) => {
        const { value } = e.target;
        try {
            const parsedJson = value.trim() === '' ? {} : JSON.parse(value);
            setSelectedChannel(prev => ({ ...prev, lorebook: parsedJson }));
            setLorebookError(null);
        } catch (err) {
            setLorebookError('Invalid JSON format.');
        }
    };

    const handleFormSubmit = async (e) => {
        e.preventDefault();
        if (!selectedChannel || !selectedChannel.name || !selectedServer) {
            setError("Server and Channel name are required.");
            return;
        }
        if (lorebookError) {
            setError("Cannot save, lorebook contains invalid JSON.");
            return;
        }

        setIsLoading(true);
        setError(null);

        const url = `${API_BASE_URL}/servers/${selectedServer}/channels/${selectedChannel.name}`;
        const method = isCreatingNew ? 'POST' : 'PUT';

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(selectedChannel),
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || `Failed to ${isCreatingNew ? 'create' : 'update'} channel.`);
            }

            await fetchChannels(selectedServer); // Refresh channel list
            setIsCreatingNew(false);
            // If creating, we might also need to refresh the server list if it was a new server
            if (!servers.includes(selectedServer)) {
                await fetchServers();
            }

        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteChannel = async () => {
        if (!selectedChannel || !selectedServer) return;

        if (confirm(`Are you sure you want to delete channel '${selectedChannel.name}' from server '${selectedServer}'?`)) {
            setIsLoading(true);
            setError(null);
            try {
                const response = await fetch(`${API_BASE_URL}/servers/${selectedServer}/channels/${selectedChannel.name}`, {
                    method: 'DELETE',
                });
                if (!response.ok) {
                    const errData = await response.json();
                    throw new Error(errData.detail || 'Failed to delete channel.');
                }
                setSelectedChannel(null);
                setIsCreatingNew(false);
                await fetchChannels(selectedServer); // Refresh list
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        }
    };

    // --- Render Logic ---

    return html`
        <div class="flex h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 font-sans">
            {/* Servers Column */}
            <aside class="w-1/5 bg-gray-50 dark:bg-gray-800 p-4 border-r border-gray-200 dark:border-gray-700 flex flex-col">
                <h2 class="text-xl font-bold mb-4">Servers</h2>
                <button onClick=${handleNewServerClick} class="btn btn-primary mb-4 w-full">
                    <i class="fas fa-plus mr-2"></i>New Server
                </button>
                <ul class="overflow-y-auto flex-grow">
                    ${servers.map(name => html`
                        <li key=${name}>
                            <button
                                onClick=${() => handleSelectServer(name)}
                                class="w-full text-left p-2 rounded-md transition-colors duration-200 ${selectedServer === name ? 'bg-blue-500 text-white' : 'hover:bg-gray-200 dark:hover:bg-gray-700'}"
                            >
                                <i class="fas fa-server mr-2"></i>${name}
                            </button>
                        </li>
                    `)}
                </ul>
            </aside>

            {/* Channels Column */}
            <aside class="w-1/5 bg-white dark:bg-gray-800 p-4 border-r border-gray-200 dark:border-gray-700 flex flex-col">
                 <h2 class="text-xl font-bold mb-4">Channels</h2>
                 <button onClick=${handleNewChannelClick} class="btn btn-secondary mb-4 w-full" disabled=${!selectedServer}>
                    <i class="fas fa-plus mr-2"></i>New Channel
                </button>
                ${selectedServer && html`
                    <ul class="overflow-y-auto flex-grow">
                        ${channels.map(name => html`
                            <li key=${name}>
                                <button
                                    onClick=${() => handleSelectChannel(name)}
                                    class="w-full text-left p-2 rounded-md transition-colors duration-200 ${selectedChannel?.name === name && !isCreatingNew ? 'bg-blue-500 text-white' : 'hover:bg-gray-200 dark:hover:bg-gray-700'}"
                                >
                                    <i class="fas fa-hashtag mr-2"></i>${name}
                                </button>
                            </li>
                        `)}
                    </ul>
                `}
                 ${!selectedServer && html`<p class="text-gray-500 text-center mt-4">Select a server to see its channels.</p>`}
            </aside>

            {/* Main Content: Channel Editor */}
            <main class="w-3/5 p-8 overflow-y-auto">
                ${isLoading && html`<${Spinner} />`}
                ${error && html`<${Alert} message=${error} />`}

                ${!isLoading && !selectedChannel && !isCreatingNew && html`
                    <div class="flex items-center justify-center h-full text-gray-500">
                        <p>${selectedServer ? 'Select a channel to edit or create a new one.' : 'Select a server to get started.'}</p>
                    </div>
                `}

                ${(selectedChannel || isCreatingNew) && !isLoading && html`
                    <form onSubmit=${handleFormSubmit}>
                        <div class="space-y-4">
                            <div>
                                <label for="name" class="label">Channel Name</label>
                                <input type="text" id="name" name="name" value=${selectedChannel.name} onInput=${handleInputChange} class="input" required disabled=${!isCreatingNew} />
                                ${!isCreatingNew && html`<p class="text-xs text-gray-500 mt-1">Channel name cannot be changed after creation.</p>`}
                            </div>
                            <div>
                                <label for="instruction" class="label">Instruction</label>
                                <textarea id="instruction" name="instruction" rows="4" value=${selectedChannel.instruction} onInput=${handleInputChange} class="input font-mono"></textarea>
                            </div>
                            <div>
                                <label for="location" class="label">Location</label>
                                <input type="text" id="location" name="location" value=${selectedChannel.location} onInput=${handleInputChange} class="input" />
                            </div>
                             <div>
                                <label for="globalvar" class="label">Global Variables (one per line)</label>
                                <textarea id="globalvar" name="globalvar" rows="3" value=${selectedChannel.globalvar} onInput=${handleInputChange} class="input font-mono"></textarea>
                            </div>
                            <div>
                                <label for="whitelist" class="label">Whitelist (one character name per line)</label>
                                <textarea id="whitelist" name="whitelist" rows="4" value=${selectedChannel.whitelist.join('\n')} onInput=${handleListChange} class="input font-mono"></textarea>
                            </div>
                            <div>
                                <label for="lorebook" class="label">Lorebook (JSON format)</label>
                                <textarea
                                    id="lorebook"
                                    name="lorebook"
                                    rows="8"
                                    value=${JSON.stringify(selectedChannel.lorebook, null, 2)}
                                    onInput=${handleLorebookChange}
                                    class="input font-mono ${lorebookError ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : ''}"
                                ></textarea>
                                ${lorebookError && html`<p class="text-xs text-red-500 mt-1">${lorebookError}</p>`}
                            </div>
                        </div>

                        <div class="mt-6 flex justify-end space-x-3">
                            ${!isCreatingNew && html`
                                <button type="button" onClick=${handleDeleteChannel} class="btn btn-danger">
                                    <i class="fas fa-trash-alt mr-2"></i>Delete Channel
                                </button>
                            `}
                            <button type="submit" class="btn btn-success">
                                <i class="fas fa-save mr-2"></i>${isCreatingNew ? 'Create Channel' : 'Save Changes'}
                            </button>
                        </div>
                    </form>
                `}
            </main>
        </div>
    `;
}
