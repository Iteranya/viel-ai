// App.js

import { h } from 'https://esm.sh/preact';
import { useState } from 'https://esm.sh/preact/hooks';
import { html } from 'https://esm.sh/htm/preact';

// Import all the manager components
import { CharacterManager } from './components/CharacterManager.js';
import { ServerManager } from './components/ServerManager.js';
import { ConfigManager } from './components/ConfigManager.js';
import { DiscordBotManager } from './components/DiscordBotManager.js';

// --- SOLUTION: Define NavButton OUTSIDE of the App component ---
const NavButton = ({ view, icon, text, currentView, setCurrentView }) => {
    const isActive = currentView === view;
    const activeClasses = 'bg-blue-600 text-white';
    const inactiveClasses = 'text-gray-300 hover:bg-gray-700 hover:text-white';

    return html`
        <button
            onClick=${() => setCurrentView(view)}
            class="px-4 py-2 text-sm font-medium rounded-md transition-colors duration-200 flex items-center ${isActive ? activeClasses : inactiveClasses}"
        >
            <i class="fas ${icon} fa-fw mr-2"></i>
            ${text}
        </button>
    `;
};

// --- The Main App Component ---
export function App() {
    const [currentView, setCurrentView] = useState('characters');

    return html`
        <div class="flex flex-col h-screen bg-gray-100 dark:bg-gray-900">
            <nav class="bg-gray-800 text-white shadow-md">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex items-center justify-between h-16">
                        <div class="flex items-center">
                            <span class="font-bold text-xl">Viel Bot Dashboard</span>
                        </div>
                        <div class="flex items-center space-x-4">
                            <${NavButton} view="characters" icon="fa-user-astronaut" text="Characters" currentView=${currentView} setCurrentView=${setCurrentView} />
                            <${NavButton} view="servers" icon="fa-server" text="Servers" currentView=${currentView} setCurrentView=${setCurrentView} />
                            <${NavButton} view="config" icon="fa-cogs" text="Configuration" currentView=${currentView} setCurrentView=${setCurrentView} />
                        </div>
                    </div>
                </div>
            </nav>

            <main class="flex-grow overflow-y-hidden">
                ${currentView === 'characters' && html`<${CharacterManager} />`}
                ${currentView === 'servers' && html`<${ServerManager} />`}
                ${currentView === 'config' && html`
                    <div class="w-full h-full p-4 bg-gray-100 dark:bg-gray-900 overflow-y-auto">
                         <${ConfigManager} />
                    </div>
                `}
            </main>

            <footer class="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-inner z-10">
                <div class="p-4">
                    <${DiscordBotManager} />
                </div>
            </footer>
        </div>
    `;
}
