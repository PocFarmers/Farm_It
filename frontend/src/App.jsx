import { useMatrixData } from './hooks/useMatrixData';
import { MatrixGrid } from './components/MatrixGrid';
import { LoadingState } from './components/LoadingState';
import { GameProvider } from './context/GameContext';
import { ResourceDisplay } from './components/ResourceDisplay';
import { TileActionModal } from './components/TileActionModal';
import { NextStepButton } from './components/NextStepButton';
import { GameOverScreen } from './components/GameOverScreen';
import { GameInitScreen } from './components/GameInitScreen';
import Chatbot from './components/Chatbot';

function App() {
    const { data, loading, error, refreshMap } = useMatrixData();

    if (loading) {
        return <LoadingState />;
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-[#F5F2EA]">
                <div className="bg-white rounded-lg p-8 shadow-2xl text-center max-w-md border-4 border-[#A37039]">
                    <h2 className="text-2xl font-bold mb-3 text-[#A37039]">Connection Error</h2>
                    <p className="text-[#35613F]">{error}</p>
                    <p className="mt-4 text-sm text-[#A37039]">Make sure the server is running</p>
                </div>
            </div>
        );
    }

    if (!data) {
        return <div>Aucune donnée disponible</div>;
    }

    return (
        <GameProvider refreshMap={refreshMap}>
            <div className="min-h-screen bg-[#F5F2EA] overflow-hidden">
                {/* Header - Agricultural Theme */}
                <header className="bg-[#35613F] text-white px-6 py-4 shadow-lg">
                    <div className="flex items-center justify-between max-w-7xl mx-auto">
                        <div className="flex items-center gap-4">
                            <img src="/logo.png" alt="Farm It Logo" className="h-12 w-12 object-contain" />
                            <div>
                                <h1 className="text-3xl font-bold tracking-tight">Farm It</h1>
                                <p className="text-sm text-[#F5F2EA] opacity-90">{data.shape[0]}x{data.shape[1]} tiles</p>
                            </div>
                        </div>
                        <ResourceDisplay />
                    </div>
                </header>

                {/* Game View */}
                <MatrixGrid data={data} layers={data.layers} />

                {/* Next Step Button - Bottom Center */}
                <NextStepButton />

                {/* Tile Action Modal */}
                <TileActionModal />

                {/* Game Over Screen */}
                <GameOverScreen />

                {/* Game Initialization Screen */}
                <GameInitScreen />

                {/* Chatbot */}
                <Chatbot apiUrl="http://localhost:8000/chat" />
            </div>
        </GameProvider>
    );
}

export default App;
