"use client";

import { useEffect, useState, useRef } from "react";
import { Loader2, Navigation, Target, Filter } from "lucide-react";
import { toast } from "react-hot-toast";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

interface TenderMarker {
    id: number;
    title: string;
    budget: number;
    category: string | null;
    region: string;
    lat: number;
    lng: number;
}

export default function RadarPage() {
    const [tenders, setTenders] = useState<TenderMarker[]>([]);
    const [loading, setLoading] = useState(true);
    const mapRef = useRef<HTMLDivElement>(null);
    const leafletMap = useRef<any>(null);

    const [isLocked, setIsLocked] = useState(false);

    useEffect(() => {
        // Загружаем CSS и JS для Leaflet динамически через CDN
        const loadLeaflet = async () => {
            if (!document.getElementById("leaflet-css")) {
                const link = document.createElement("link");
                link.id = "leaflet-css";
                link.rel = "stylesheet";
                link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
                document.head.appendChild(link);
            }

            if (!document.getElementById("leaflet-js")) {
                const script = document.createElement("script");
                script.id = "leaflet-js";
                script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
                script.async = true;
                script.onload = () => {
                   fetchTenders();
                };
                document.body.appendChild(script);
            } else if ((window as any).L) {
                fetchTenders();
            }
        };

        loadLeaflet();

        return () => {
            if (leafletMap.current) {
                leafletMap.current.remove();
            }
        };
    }, []);

    const fetchTenders = async () => {
        try {
            let tgId = 0;
            if (typeof window !== "undefined" && (window as any).Telegram?.WebApp?.initDataUnsafe?.user?.id) {
                tgId = (window as any).Telegram.WebApp.initDataUnsafe.user.id;
            }

            const res = await fetch(`${API_BASE}/api/v1/tenders/map?telegram_id=${tgId}`);
            const data = await res.json();
            
            if (data.ok) {
                setTenders(data.map_tenders);
                initMap(data.map_tenders);
            } else if (data.error === "b2b_locked") {
                setIsLocked(true);
                // Показываем демо маркеры на размытом фоне
                initMap(data.map_tenders || [
                    {"id": 9991, "title": "Аэрофотосъемка нефтепровода 'Восток'", "budget": 1250000, "category": "Мониторинг", "region": "ХМАО", "lat": 61.0, "lng": 69.0},
                    {"id": 9992, "title": "Опрыскивание полей 500 Га", "budget": 950000, "category": "Агро", "region": "Краснодарский край", "lat": 45.03, "lng": 38.97}
                ]);
            }
        } catch (e) {
            toast.error("Не удалось загрузить данные радара");
        } finally {
            setLoading(false);
        }
    };

    const initMap = (markers: TenderMarker[]) => {
        const L = (window as any).L;
        if (!L || !mapRef.current) return;

        if (!leafletMap.current) {
            leafletMap.current = L.map(mapRef.current, { zoomControl: false }).setView([55.751244, 37.618423], 5);
            L.control.zoom({ position: "bottomright" }).addTo(leafletMap.current);
            
            // Используем темную тему карты (CartoDB Dark Matter)
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '&copy; OpenStreetMap &copy; CartoDB',
                subdomains: 'abcd',
                maxZoom: 20
            }).addTo(leafletMap.current);
        }

        const map = leafletMap.current;

        // Custom Gold Icon for Tenders
        const goldIcon = L.divIcon({
            className: 'custom-icon',
            html: `<div class="w-8 h-8 bg-gradient-to-br from-khokhloma-gold to-yellow-600 rounded-full border-2 border-white flex items-center justify-center shadow-[0_0_15px_rgba(255,215,0,0.5)] animate-pulse"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div>`,
            iconSize: [32, 32],
            iconAnchor: [16, 16],
            popupAnchor: [0, -16]
        });

        markers.forEach(t => {
            L.marker([t.lat, t.lng], { icon: goldIcon })
                .addTo(map)
                .bindPopup(`
                    <div class="p-2 font-sans bg-[#121214] border border-white/10 rounded-lg text-white w-64">
                        <div class="text-[10px] text-khokhloma-gold font-bold uppercase mb-1">${t.category || "Общее"}</div>
                        <h3 class="font-bold text-sm mb-2 leading-tight">${t.title}</h3>
                        <div class="text-xl font-black text-emerald-400 mb-3">${t.budget.toLocaleString()} ₽</div>
                        <a href="/dashboard/b2g" class="block w-full text-center bg-white text-black font-bold py-2 rounded-lg text-xs hover:bg-gray-200 transition-colors">Подать заявку</a>
                    </div>
                `, {
                    className: 'dark-popup' 
                });
        });

        if (markers.length > 0) {
            const bounds = L.latLngBounds(markers.map(m => [m.lat, m.lng]));
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    };

    const handleLocateMe = () => {
        if (!navigator.geolocation) {
            toast.error("Геолокация не поддерживается вашим браузером");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                const L = (window as any).L;
                if (leafletMap.current && L) {
                    leafletMap.current.setView([latitude, longitude], 10);
                    L.circle([latitude, longitude], {
                        color: '#3b82f6',
                        fillColor: '#3b82f6',
                        fillOpacity: 0.2,
                        radius: 5000 
                    }).addTo(leafletMap.current);
                    toast.success("Ваша позиция найдена!");
                }
            },
            () => toast.error("Не удалось получить геопозицию")
        );
    };

    return (
        <div className="flex flex-col h-[calc(100vh-80px)] relative overflow-hidden bg-black/50">
            {/* Header / Panel overlay */}
            <div className={`absolute top-4 left-4 right-4 z-[400] flex justify-between items-start pointer-events-none transition-all duration-500 ${isLocked ? 'blur-md opacity-30 select-none' : ''}`}>
                <div className="bg-[#121214]/90 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-2xl pointer-events-auto max-w-xs">
                    <h1 className="text-xl font-black text-white flex items-center gap-2 mb-1">
                        <Target className="w-5 h-5 text-khokhloma-gold" /> Радар B2G
                    </h1>
                    <p className="text-xs text-gray-400 mb-4">Найдено {tenders.length} активных тендеров поблизости.</p>
                    
                    <button 
                        onClick={handleLocateMe}
                        disabled={isLocked}
                        className="w-full flex items-center justify-center gap-2 bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 border border-blue-500/30 rounded-xl py-2 px-4 transition-all text-sm font-bold disabled:opacity-50"
                    >
                        <Navigation className="w-4 h-4" /> Найти меня
                    </button>
                </div>
            </div>

            {loading && (
                <div className="absolute inset-0 z-[500] bg-black/80 flex flex-col justify-center items-center">
                    <Loader2 className="w-12 h-12 text-khokhloma-gold animate-spin" />
                    <p className="mt-4 text-white font-bold tracking-widest uppercase text-sm">Сканирование радара...</p>
                </div>
            )}

            {/* Замок для B2B */}
            {isLocked && !loading && (
                <div className="absolute inset-0 z-[500] bg-black/40 backdrop-blur-[8px] flex flex-col justify-center items-center px-4 animate-in fade-in duration-700">
                    <div className="bg-[#121214]/90 border box-shadow-xl border-khokhloma-gold/30 rounded-3xl p-8 max-w-md text-center shadow-[0_0_50px_rgba(255,215,0,0.1)]">
                        <div className="w-20 h-20 bg-khokhloma-gold/10 border border-khokhloma-gold/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
                            <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-khokhloma-gold"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                        </div>
                        <h2 className="text-2xl font-black text-white mb-3">Радар Заблокирован</h2>
                        <p className="text-gray-400 text-sm mb-6 leading-relaxed">
                            Интерактивный Радар B2G позволяет отслеживать самые прибыльные госзаказы по вашей геолокации. 
                            <br/><br/>
                            Доступ предоставляется <strong className="text-white">только верифицированным ИП и Юридическим Лицам</strong>. Добавьте ИНН в профиле, чтобы открыть карту.
                        </p>
                        <a href="/dashboard/legal" className="inline-block w-full bg-khokhloma-gold hover:bg-yellow-600 text-black font-black uppercase tracking-wider py-3 px-6 rounded-xl transition-all shadow-[0_0_20px_rgba(255,215,0,0.3)]">
                            Верифицировать Юр. Лицо
                        </a>
                    </div>
                </div>
            )}

            {/* Map Container */}
            <div ref={mapRef} className={`w-full h-full z-[100] outline-none transition-all duration-1000 ${isLocked ? 'grayscale opacity-50 blur-[2px] pointer-events-none' : ''}`} style={{ backgroundColor: "#0A0A0B" }} />

            {/* Additional global styles for mapping */}
            <style jsx global>{`
                .leaflet-container { font-family: inherit; }
                .leaflet-popup-content-wrapper { background: transparent; padding: 0; border-radius: 0; box-shadow: none; }
                .leaflet-popup-tip-container { display: none; }
                .dark-popup .leaflet-popup-content { margin: 0; }
                .dark-popup .leaflet-popup-close-button { color: white !important; top: 10px !important; right: 10px !important; }
            `}</style>
        </div>
    );
}
