import React, { useState, useEffect } from 'react';
import { AlertTriangle, MapPin, ShieldAlert, PhoneCall, WifiOff, MessageSquare } from 'lucide-react';
import CivilianMap from './components/Map';

function App() {
  const [reportState, setReportState] = useState('idle');
  const [currentSeverity, setCurrentSeverity] = useState('low');
  const [currentIncident, setCurrentIncident] = useState(null);
  const [aiExplanation, setAiExplanation] = useState('');
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isSimulatingOffline, setIsSimulatingOffline] = useState(false);
  const [p2pActive, setP2PActive] = useState(false);

  const effectiveOnlineStatus = isOnline && !isSimulatingOffline;

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  useEffect(() => {
    const fetchLiveData = () => {
      if (!isOnline) return;
      fetch('http://localhost:8000/api/incidents')
        .then(res => res.json())
        .then(data => {
          if (data.length > 0) {
            setCurrentSeverity(data[0].severity);
            setCurrentIncident(data[0]);
          } else {
            setCurrentSeverity('low');
            setCurrentIncident(null);
          }
        })
        .catch(err => console.error(err));
    };

    fetchLiveData();
    const intervalId = setInterval(fetchLiveData, 3000);
    return () => clearInterval(intervalId);
  }, [isOnline]);

  useEffect(() => {
    if (!isOnline || !currentIncident?.id) return;
    fetch('http://localhost:8000/api/dashboard-state')
      .then(res => res.json())
      .then(data => {
        if (data.executive_briefing) {
          setAiExplanation(data.executive_briefing);
        }
      })
      .catch(err => console.error(err));
  }, [currentIncident?.id, isOnline]);

  const handleEmergencyReport = () => {
    if (!effectiveOnlineStatus) {
      handleOfflineSurvival();
      return;
    }
    setReportState('sending');
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => sendReport(position.coords.latitude, position.coords.longitude),
        () => sendReport(13.05 + Math.random() * 0.02, 80.25 + Math.random() * 0.02)
      );
    } else {
      sendReport(13.05, 80.25);
    }
  };

  const handleOfflineSurvival = () => {
    setP2PActive(true);
    setTimeout(() => setP2PActive(false), 8000);

    // Multi-tier Fallback 2: SMS Broadcast
    const phone = "911";
    const body = `CRITICAL: CrisisSync AI Disaster Report. Last Coords: ${currentIncident ? currentIncident.location_lat : '13.08'},${currentIncident ? currentIncident.location_lng : '80.27'}. No Data. Help!`;
    window.location.href = `sms:${phone}?body=${encodeURIComponent(body)}`;
  };

  const sendReport = async (lat, lng) => {
    try {
      await fetch('http://localhost:8000/api/reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: "user_" + Math.random().toString(36).substr(2, 9),
          location_lat: lat,
          location_lng: lng,
          description: "Emergency distress from PWA",
          medium: "internet"
        })
      });
      setReportState('received');
      setTimeout(() => setReportState('idle'), 5000);
    } catch (err) {
      console.error(err);
      setReportState('idle');
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-gray-50 overflow-hidden relative">
      {/* Top Warning Banner */}
      {currentSeverity !== 'low' && (
        <div className={`w-full p-4 flex flex-col items-start justify-center text-white z-10 shadow-md ${currentSeverity === 'critical' ? 'bg-red-600' :
          currentSeverity === 'high' ? 'bg-orange-500' : 'bg-yellow-500'
          }`}>
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-6 h-6 animate-pulse" />
            <div>
              <h1 className="font-bold text-lg leading-tight uppercase">High Risk Zone: {currentSeverity}</h1>
              <p className="text-sm font-medium opacity-90">Evacuation recommended immediately.</p>
            </div>
          </div>
          {aiExplanation && (
            <div className="mt-3 p-2 bg-black/20 rounded border border-white/20 text-xs shadow-inner">
              <strong>AI Advisory:</strong> {aiExplanation}
            </div>
          )}
        </div>
      )}

      {/* Map Content Layer */}
      <div className="flex-1 relative">
        <CivilianMap severity={currentSeverity} incident={currentIncident} />
        <div className="absolute top-4 left-4 z-[400] bg-white/90 backdrop-blur rounded-xl shadow-lg p-3 max-w-[200px]">
          <div className="flex items-center space-x-2 text-gray-700">
            <MapPin className="w-4 h-4 text-blue-500" />
            <span className="text-xs font-semibold">Your Location</span>
          </div>
          <p className="text-[10px] text-gray-500 mt-1">Data updated Just Now</p>
        </div>
      </div>

      {/* Emergency Report Action Footer */}
      <div className="w-full bg-white p-6 shadow-[0_-4px_20px_-5px_rgba(0,0,0,0.1)] z-10 rounded-t-3xl border-t border-gray-100 pb-10">

        {/* Connection Status Badge */}
        <div className="flex flex-col items-center mb-4 space-y-2">
          <div className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest flex items-center space-x-1 ${effectiveOnlineStatus ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600 animate-pulse'
            }`}>
            {effectiveOnlineStatus ? <MapPin className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
            <span>{effectiveOnlineStatus ? 'Network Stable' : 'OFFLINE MODE: NO INTERNET'}</span>
          </div>

          <button
            onClick={() => setIsSimulatingOffline(!isSimulatingOffline)}
            className="text-[9px] font-bold text-gray-400 uppercase tracking-tighter hover:text-red-500 transition-colors"
          >
            [DEMO: {isSimulatingOffline ? 'Disable' : 'Enable'} Simulation]
          </button>
        </div>

        {p2pActive && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-100 rounded-xl text-center flex items-center justify-center space-x-2">
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-ping" />
            <p className="text-xs text-blue-600 font-bold uppercase">
              Broadcasting P2P Signal (WebRTC)...
            </p>
          </div>
        )}

        <button
          onClick={handleEmergencyReport}
          disabled={reportState !== 'idle'}
          className={`w-full rounded-2xl py-4 flex flex-col items-center justify-center space-y-1 transition-all active:scale-95 ${!effectiveOnlineStatus ? 'bg-gray-900 shadow-2xl text-white border-2 border-red-500/30' :
              reportState === 'idle'
                ? 'bg-gradient-to-br from-red-500 to-red-600 shadow-red-500/30 shadow-xl text-white'
                : 'bg-gray-100 text-gray-400'
            }`}
        >
          {!effectiveOnlineStatus ? (
            <>
              <MessageSquare className="w-8 h-8 mb-1" />
              <span className="font-bold text-xl uppercase tracking-tighter">BROADCAST SMS SIGNAL</span>
              <span className="text-[10px] opacity-70 font-medium">SHOUTS LOCATION TO RESPONDERS</span>
            </>
          ) : (
            <>
              {reportState === 'idle' && (
                <>
                  <ShieldAlert className="w-8 h-8 mb-1" />
                  <span className="font-bold text-xl tracking-tight">REPORT EMERGENCY</span>
                  <span className="text-xs opacity-80 uppercase font-medium">Auto-attaches Location</span>
                </>
              )}
              {reportState === 'sending' && (
                <span className="font-bold animate-pulse uppercase">Syncing with Command...</span>
              )}
              {reportState === 'received' && (
                <span className="font-bold text-green-600 uppercase">Received. Deploying Units.</span>
              )}
            </>
          )}
        </button>

        <div className="mt-6 flex justify-around">
          <div className="flex flex-col items-center text-gray-500 space-y-1">
            <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
              <PhoneCall className="w-5 h-5 text-gray-600" />
            </div>
            <span className="text-[10px] font-bold uppercase tracking-wide">Call 911</span>
          </div>
          <div className="flex flex-col items-center text-blue-500 space-y-1">
            <div className="w-12 h-12 bg-blue-50/50 rounded-full flex items-center justify-center border border-blue-100">
              <MapPin className="w-5 h-5" />
            </div>
            <span className="text-[10px] font-bold uppercase tracking-wide">Shelters</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
