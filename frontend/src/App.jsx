import { useMatrixData } from './hooks/useMatrixData';
import { MatrixGrid } from './components/MatrixGrid';
import { LoadingState } from './components/LoadingState';

function App() {
  const { data, loading, error } = useMatrixData();

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-b from-sky-400 to-blue-600">
        <div className="bg-white/90 backdrop-blur-sm rounded-lg p-8 shadow-2xl text-center max-w-md">
          <h2 className="text-2xl font-bold mb-3 text-red-600">🌊 Erreur de connexion</h2>
          <p className="text-gray-700">{error}</p>
          <p className="mt-4 text-sm text-gray-500">Assurez-vous que le serveur est démarré</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return <div>Aucune donnée disponible</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-400 via-sky-500 to-blue-600 overflow-hidden">
      {/* Header - Game UI Style */}
      <header className="bg-gradient-to-r from-green-600 to-emerald-700 text-white px-6 py-3 shadow-lg border-b-4 border-green-800">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🏝️</span>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Farm It</h1>
              <p className="text-xs text-green-200">Votre île • {data.shape[0]}x{data.shape[1]} tuiles</p>
            </div>
          </div>
          <div className="flex gap-4 text-sm">
            <div className="bg-white/20 px-3 py-1 rounded-full backdrop-blur-sm">
              <span className="font-semibold">🌡️ Température</span>
            </div>
            <div className="bg-white/20 px-3 py-1 rounded-full backdrop-blur-sm">
              <span className="font-semibold">💧 Humidité</span>
            </div>
          </div>
        </div>
      </header>

      {/* Game View */}
      <MatrixGrid data={data} layers={data.layers} />
    </div>
  );
}

export default App;
