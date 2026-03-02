import React from 'react';
import { Activity, AlertTriangle, CloudRain, Flame, Radio, Users } from 'lucide-react';
import DashboardMap from './components/DashboardMap';

const SeverityCard = ({ title, score, icon: Icon, trend, colorClass }) => (
  <div className={`p-4 rounded-xl border border-gray-800 bg-gray-900/50 backdrop-blur flex flex-col justify-between ${colorClass}`}>
    <div className="flex justify-between items-start">
      <div className="flex items-center space-x-2">
        <Icon className="w-5 h-5 opacity-70" />
        <span className="font-semibold text-gray-300 tracking-wide text-sm uppercase">{title}</span>
      </div>
      {trend === 'up' ?
        <span className="text-red-500 text-xs font-bold px-2 py-1 bg-red-500/10 rounded">↑ Rising</span> :
        <span className="text-gray-500 text-xs font-bold px-2 py-1 bg-gray-800 rounded">→ Stable</span>
      }
    </div>
    <div className="mt-4 flex items-end justify-between">
      <div className="text-4xl font-black tracking-tighter">{score}</div>
      <div className="text-xs text-gray-500 pb-1">/ 100</div>
    </div>
  </div>
);

function App() {
  const [dashboardState, setDashboardState] = React.useState(null);
  const [incidents, setIncidents] = React.useState([]);
  const [reports, setReports] = React.useState([]);
  const [dispatchInfo, setDispatchInfo] = React.useState(null);

  React.useEffect(() => {
    const fetchLiveData = () => {
      // Fetch active incidents
      fetch('http://localhost:8000/api/incidents')
        .then(res => res.json())
        .then(data => setIncidents(data))
        .catch(err => console.error("Error fetching incidents:", err));

      // Fetch emergency reports 
      fetch('http://localhost:8000/api/reports')
        .then(res => res.json())
        .then(data => setReports(data))
        .catch(err => console.error("Error fetching reports:", err));
    };

    fetchLiveData(); // Initial fetch
    const intervalId = setInterval(fetchLiveData, 3000); // Poll every 3 seconds
    return () => clearInterval(intervalId);
  }, []);

  // Fetch AI Intelligence Briefs Only Once Per Incident to avoid AI Rate Limits
  React.useEffect(() => {
    // 1. Fetch Global Executive State Summary
    fetch('http://localhost:8000/api/dashboard-state')
      .then(res => res.json())
      .then(data => setDashboardState(data))
      .catch(err => console.error("Error fetching dashboard state:", err));

    // 2. Fetch Dispatch Recommendation for Primary Incident
    if (incidents.length > 0) {
      const primaryId = incidents[0].id;
      fetch(`http://localhost:8000/api/incidents/${primaryId}/recommendation`)
        .then(res => {
          if (!res.ok) throw new Error('API Rate Limited or error');
          return res.json();
        })
        .then(recData => setDispatchInfo(recData))
        .catch(err => console.error("AI Dispatch Fetch Error:", err));
    } else {
      setDispatchInfo(null);
    }
  }, [incidents.length > 0 ? incidents[0].id : null]);

  return (
    <div className="min-h-screen bg-black text-gray-100 p-4 font-sans selection:bg-red-500/30">

      {/* Top Navigation / Status Bar */}
      <header className="flex justify-between items-center mb-6 px-2">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-red-600 flex items-center justify-center shadow-[0_0_15px_rgba(220,38,38,0.5)]">
            <Radio className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl font-black tracking-tight leading-none uppercase">CrisisSync AI</h1>
            <p className="text-xs text-gray-500 font-medium">Operations Dashboard</p>
          </div>
        </div>
        <div className="flex space-x-4">
          <div className="flex items-center space-x-2 text-xs font-semibold bg-gray-900 border border-gray-800 px-3 py-1.5 rounded-full">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-gray-400">System Online</span>
          </div>
        </div>
      </header>

      {/* 4 Severity Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 text-white lg:grid-cols-4 gap-4 mb-6">
        <SeverityCard title="Flood Risk" score={24} icon={CloudRain} trend="stable" colorClass="hover:border-blue-500/50 transition-colors" />
        <SeverityCard title="Earthquake" score={85} icon={Activity} trend="up" colorClass="bg-red-950/30 border-red-900/50 shadow-[0_0_20px_rgba(220,38,38,0.1)]" />
        <SeverityCard title="Wildfire" score={42} icon={Flame} trend="stable" colorClass="hover:border-orange-500/50 transition-colors" />
        <SeverityCard title="Storm" score={12} icon={AlertTriangle} trend="stable" colorClass="hover:border-yellow-500/50 transition-colors" />
      </div>

      {/* AI Intelligence Brief */}
      {dashboardState && dashboardState.executive_briefing && (
        <div className="mb-6 p-4 rounded-xl border border-blue-900/50 bg-blue-950/20">
          <h2 className="text-sm font-bold text-blue-400 tracking-widest uppercase mb-2">AI Executive Briefing</h2>
          <p className="text-gray-300 text-sm">{dashboardState.executive_briefing}</p>
          {dashboardState.technial_operations_report && (
            <p className="text-gray-400 text-xs mt-2 italic">{dashboardState.technical_operations_report}</p>
          )}
        </div>
      )}

      {/* Main Content Split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-220px)]">

        {/* Left Column: Active Incidents & Ticker */}
        <div className="flex flex-col space-y-6 overflow-hidden">

          {/* AI Responder Dispatch Pane */}
          {dispatchInfo && (
            <div className="bg-orange-950/20 border border-orange-900/50 rounded-xl flex flex-col shrink-0 shadow-[0_0_15px_rgba(234,88,12,0.1)]">
              <div className="p-3 border-b border-orange-900/50 flex justify-between items-center bg-orange-950/40 backdrop-blur">
                <h2 className="font-bold text-sm tracking-widest text-orange-400 uppercase">Responder Dispatch</h2>
              </div>
              <div className="p-4 space-y-3 overflow-y-auto max-h-[350px]">
                <div>
                  <span className="text-xs text-orange-500 font-bold uppercase">Primary Action</span>
                  <p className="text-sm text-gray-200 mt-1 font-medium">{dispatchInfo.primary_action}</p>
                </div>
                <div className="grid grid-cols-2 gap-3 mt-3">
                  <div className="bg-black/30 p-2 rounded border border-gray-800">
                    <span className="text-[10px] text-gray-500 font-bold uppercase">Route</span>
                    <p className="text-xs text-gray-300 mt-1 truncate" title={dispatchInfo.recommended_route}>{dispatchInfo.recommended_route}</p>
                  </div>
                  <div className="bg-black/30 p-2 rounded border border-gray-800">
                    <span className="text-[10px] text-gray-500 font-bold uppercase">Time limit</span>
                    <p className="text-xs text-gray-300 mt-1 truncate">{dispatchInfo.estimated_time_to_impact}</p>
                  </div>
                </div>
                <div className="mt-2">
                  <span className="text-xs text-orange-500 font-bold uppercase">Required Equipment</span>
                  <ul className="list-disc list-inside text-xs text-gray-300 mt-1 space-y-1">
                    {dispatchInfo.recommended_resources?.map((res, i) => <li key={i}>{res}</li>)}
                  </ul>
                </div>
              </div>
            </div>
          )}

          <div className="flex-1 bg-gray-900 border border-gray-800 rounded-xl flex flex-col overflow-hidden">
            <div className="p-4 border-b border-gray-800 flex justify-between items-center bg-gray-900/80 backdrop-blur z-10">
              <h2 className="font-bold text-sm tracking-widest text-gray-400 uppercase">Active Incidents</h2>
              <span className="bg-red-500/20 text-red-400 text-xs px-2 py-0.5 rounded font-bold">{incidents.length} Active</span>
            </div>
            <div className="overflow-y-auto p-4 space-y-3">
              {incidents.length === 0 && <p className="text-xs text-gray-500">No active incidents found.</p>}
              {incidents.map((incident) => (
                <div key={incident.id} className="p-3 rounded-lg border border-red-900/50 bg-red-950/20 cursor-pointer hover:bg-red-900/30 transition-all">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-red-400 text-sm">{incident.disaster_type} • {incident.location_name}</h3>
                    <span className="text-[10px] text-gray-500 bg-black/50 px-2 py-0.5 rounded">ID: {incident.id}</span>
                  </div>
                  <div className="flex items-center space-x-4 text-xs text-gray-400">
                    <div className="flex items-center space-x-1">
                      <Users className="w-3 h-3" />
                      <span>~{incident.population_affected} at risk</span>
                    </div>
                    <div className={`font-semibold text-[10px] uppercase ${incident.severity === 'critical' ? 'text-red-500' : 'text-orange-400'}`}>
                      Severity: {incident.severity}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Right Column: Interactive Map (Takes up 2 cols) */}
        <div className="lg:col-span-2 relative">
          <DashboardMap incidents={incidents} reports={reports} />
        </div>

      </div>

    </div>
  );
}

export default App;
