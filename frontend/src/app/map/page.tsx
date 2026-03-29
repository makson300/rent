"use client";

import { useState, useEffect, useMemo } from "react";
import { Map, Overlay, ZoomControl } from "pigeon-maps";
import { AlertCircle, Navigation, Shield, Layers, Plane } from "lucide-react";
import Link from "next/link";
import { toast } from "react-hot-toast";
import { NOFLY_ZONES } from "@/data/nofly-zones";

export default function InteractiveMapPage() {
  const [filter, setFilter] = useState("all");
  const [selectedMarker, setSelectedMarker] = useState<any>(null);
  const [selectedZone, setSelectedZone] = useState<any>(null);
  const [markers, setMarkers] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showNoflyZones, setShowNoflyZones] = useState(true);
  const [zoom, setZoom] = useState(10);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/radar/markers`)
      .then(r => r.json())
      .then(data => {
        setMarkers(data);
        setIsLoading(false);
      })
      .catch(e => {
        console.error("Failed to fetch markers", e);
        setIsLoading(false);
        toast.error("Не удалось загрузить данные Радара");
      });
  }, []);

  const filteredMarkers = markers.filter(m => filter === "all" || m.type === filter);

  /** Convert km radius to approximate pixel size based on zoom */
  const radiusToPixels = (radiusKm: number, lat: number) => {
    const metersPerPixel = (156543.03392 * Math.cos((lat * Math.PI) / 180)) / Math.pow(2, zoom);
    return Math.max(8, (radiusKm * 1000) / metersPerPixel);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-80px)]">
      {/* Header */}
      <div className="bg-[#0A0A0B] border-b border-white/10 p-4 md:p-6 shrink-0 z-10 relative">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
              <Navigation className="w-6 h-6 text-blue-400" />
              Радар SkyRent
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              Мониторинг воздушного пространства, ЧС и активных заказов.
            </p>
          </div>
          
          <div className="flex flex-wrap gap-2">
            <button 
              onClick={() => setFilter("all")} 
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${filter === "all" ? "bg-white/20 text-white" : "bg-white/5 text-gray-400 hover:bg-white/10"}`}
            >
              Все объекты
            </button>
            <button 
              onClick={() => setFilter("emergency")} 
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-1.5 ${filter === "emergency" ? "bg-red-500/20 text-red-400 border border-red-500/30" : "bg-white/5 text-gray-400 hover:bg-red-500/10 hover:text-red-400"}`}
            >
              <AlertCircle className="w-4 h-4" /> ЧС и Поиски
            </button>
            <button 
              onClick={() => setShowNoflyZones(!showNoflyZones)} 
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-1.5 ${showNoflyZones ? "bg-orange-500/20 text-orange-400 border border-orange-500/30" : "bg-white/5 text-gray-400 hover:bg-orange-500/10 hover:text-orange-400"}`}
            >
              <Plane className="w-4 h-4" /> Бесполётные зоны
            </button>
            <button 
              onClick={() => setFilter("job")} 
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-1.5 ${filter === "job" ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" : "bg-white/5 text-gray-400 hover:bg-emerald-500/10 hover:text-emerald-400"}`}
            >
              <Layers className="w-4 h-4" /> Заказы
            </button>
          </div>
        </div>
      </div>

      {/* Map */}
      <div className="flex-1 relative border-b border-white/10">
        <Map 
          defaultCenter={[55.751244, 37.618423]} 
          defaultZoom={10}
          onBoundsChanged={({ zoom: z }) => setZoom(z)}
          attributionPrefix={false}
        >
          <ZoomControl />
          
          {/* === No-Fly Zones (circles) === */}
          {showNoflyZones && NOFLY_ZONES.map((zone) => {
            const size = radiusToPixels(zone.radiusKm, zone.lat);
            return (
              <Overlay
                key={zone.id}
                anchor={[zone.lat, zone.lng]}
                offset={[size, size]}
              >
                <div
                  className="rounded-full cursor-pointer transition-opacity hover:opacity-80"
                  onClick={() => { setSelectedZone(zone); setSelectedMarker(null); }}
                  style={{
                    width: size * 2,
                    height: size * 2,
                    background: zone.type === "prohibited"
                      ? "rgba(239, 68, 68, 0.18)"
                      : "rgba(249, 115, 22, 0.14)",
                    border: zone.type === "prohibited"
                      ? "2px solid rgba(239, 68, 68, 0.5)"
                      : "2px dashed rgba(249, 115, 22, 0.4)",
                  }}
                />
              </Overlay>
            );
          })}

          {/* === Dynamic markers === */}
          {filteredMarkers.map((marker) => (
            <Overlay 
              key={marker.id} 
              anchor={[marker.lat, marker.lng]} 
              offset={[16, 32]}
            >
              <div 
                className="relative cursor-pointer group"
                onClick={() => { setSelectedMarker(marker); setSelectedZone(null); }}
              >
                {marker.type === 'emergency' && (
                  <div className="absolute -inset-2 bg-red-500/40 rounded-full animate-ping" />
                )}
                <div className={`w-8 h-8 rounded-full border-2 border-white shadow-xl flex items-center justify-center relative z-10 transition-transform group-hover:scale-110 ${
                  marker.type === 'emergency' ? 'bg-red-500' :
                  marker.type === 'nofly' ? 'bg-orange-500' : 'bg-emerald-500'
                }`}>
                  {marker.type === 'emergency' ? <AlertCircle className="w-4 h-4 text-white" /> :
                   marker.type === 'nofly' ? <Shield className="w-4 h-4 text-white" /> :
                   <Layers className="w-4 h-4 text-white" />}
                </div>
              </div>
            </Overlay>
          ))}
        </Map>

        {/* === No-Fly Zone Info Panel === */}
        {selectedZone && (
          <div className="absolute top-4 right-4 md:top-8 md:right-8 bg-[#0A0A0B]/90 backdrop-blur-md border border-white/10 p-6 rounded-2xl w-[320px] shadow-2xl z-20">
            <div className="flex justify-between items-start mb-4">
              <span className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-md bg-red-500/20 text-red-500">
                {selectedZone.type === "prohibited" ? "ЗАПРЕТ" : selectedZone.type === "airport" ? "CTR АЭРОПОРТ" : "ОГРАНИЧЕНИЕ"}
              </span>
              <button onClick={() => setSelectedZone(null)} className="text-gray-500 hover:text-white">✕</button>
            </div>
            <h3 className="text-lg font-bold text-white mb-2">{selectedZone.name}</h3>
            <p className="text-gray-400 text-sm mb-4">{selectedZone.description}</p>
            <div className="text-xs text-gray-500 mb-4 font-mono">
              📍 {selectedZone.lat.toFixed(4)}, {selectedZone.lng.toFixed(4)} • R={selectedZone.radiusKm}км
            </div>
            <Link href="/dashboard/legal" className="w-full block text-center py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold rounded-xl transition-all shadow-lg shadow-blue-500/20">
              Подать заявку на ИВП
            </Link>
          </div>
        )}

        {/* === Marker Info Panel === */}
        {selectedMarker && (
          <div className="absolute top-4 right-4 md:top-8 md:right-8 bg-[#0A0A0B]/90 backdrop-blur-md border border-white/10 p-6 rounded-2xl w-[320px] shadow-2xl z-20">
            <div className="flex justify-between items-start mb-4">
              <span className={`px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-md ${
                selectedMarker.type === 'emergency' ? "bg-red-500/20 text-red-500" :
                (selectedMarker.type === 'nofly' || selectedMarker.type === 'pending_flight') ? "bg-orange-500/20 text-orange-500" :
                "bg-emerald-500/20 text-emerald-500"
              }`}>
                {selectedMarker.type === 'emergency' ? 'Вызов ЧС' : (selectedMarker.type === 'nofly' || selectedMarker.type === 'pending_flight') ? 'ОрВД ИВП' : 'Коммерция'}
              </span>
              <button onClick={() => setSelectedMarker(null)} className="text-gray-500 hover:text-white">✕</button>
            </div>
            <h3 className="text-lg font-bold text-white mb-2">{selectedMarker.title}</h3>
            <p className="text-gray-400 text-sm mb-4">{selectedMarker.desc}</p>
            {selectedMarker.budget && (
              <div className="text-emerald-400 font-mono font-bold mb-4">Бюджет: {selectedMarker.budget}</div>
            )}
            <div className="text-xs text-gray-500 mb-6 font-mono">
              GPS: {selectedMarker.lat}, {selectedMarker.lng}
            </div>
            {selectedMarker.type === 'emergency' && (
              <Link href="https://t.me/SkyRentAdminBot" target="_blank" className="w-full block text-center py-2.5 bg-red-600 hover:bg-red-700 text-white text-sm font-bold rounded-xl transition-all shadow-lg shadow-red-500/20">
                Присоединиться к поискам
              </Link>
            )}
            {selectedMarker.type === 'job' && (
              <Link href="/jobs" className="w-full block text-center py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-bold rounded-xl transition-all shadow-lg shadow-emerald-500/20">
                Откликнуться
              </Link>
            )}
            {(selectedMarker.type === 'nofly' || selectedMarker.type === 'pending_flight') && (
              <Link href="/dashboard/legal" className="w-full block text-center py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold rounded-xl transition-all shadow-lg shadow-blue-500/20">
                Мои планы полетов (ОрВД)
              </Link>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
