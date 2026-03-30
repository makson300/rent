"use client";

import { useState, useRef } from "react";
import { CloudRain, UploadCloud, CheckCircle2, AlertCircle, FileText, Loader2 } from "lucide-react";
import DroneLoader from "@/components/DroneLoader";
import { toast } from "react-hot-toast";
import { api } from "@/lib/api";

export default function TelemetryUploadPage() {
    const [isDragging, setIsDragging] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);
    const [uploadedHours, setUploadedHours] = useState<number | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // В реальном приложении ID берется из локального стейта/сессии
    const MOCK_USER_ID = 0; 
    const [activeTab, setActiveTab] = useState<"logs" | "orvd">("logs");

    const [orvdForm, setOrvdForm] = useState({
        lat: 55.7558, lng: 37.6173, radius: 500, height: 150,
        start: new Date().toISOString().slice(0, 16),
        end: new Date(Date.now() + 7200000).toISOString().slice(0, 16),
        model: "DJI Mavic 3"
    });
    const [orvdResult, setOrvdResult] = useState<string | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);

    const handleGenerateOrvd = async () => {
        setIsGenerating(true);
        try {
            const data = await api.post<{ ok: boolean; message_format?: string; error?: string }>(
                "/airspace/plan/generate",
                {
                    lat: orvdForm.lat,
                    lng: orvdForm.lng,
                    radius: orvdForm.radius,
                    height: orvdForm.height,
                    start_time: new Date(orvdForm.start).toISOString(),
                    end_time: new Date(orvdForm.end).toISOString(),
                    drone_model: orvdForm.model,
                }
            );
            if (data.ok && data.message_format) {
                setOrvdResult(data.message_format);
                toast.success("План успешно сгенерирован и отправлен в Телеграм!");
            } else {
                toast.error(data.error || "Ошибка генерации");
            }
        } catch {
            toast.error("Сетевая ошибка");
        } finally {
            setIsGenerating(false);
        }
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            validateAndSetFile(e.dataTransfer.files[0]);
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            validateAndSetFile(e.target.files[0]);
        }
    };

    const validateAndSetFile = (selectedFile: File) => {
        // Checking for standard DJI text log formats loosely
        if (!selectedFile.name.toLowerCase().endsWith('.txt') && !selectedFile.name.toLowerCase().endsWith('.csv')) {
            toast.error("Пожалуйста, загрузите правильный лог от DJI (.txt или .csv)");
            return;
        }
        if (selectedFile.size > 50 * 1024 * 1024) { // 50MB limit
            toast.error("Файл слишком большой. Максимум 50 МБ.");
            return;
        }
        setFile(selectedFile);
    };

    const handleUpload = async () => {
        if (!file) return;

        setLoading(true);
        const formData = new FormData();
        formData.append("file", file);

        try {
            const baseUrl = process.env.NEXT_PUBLIC_API_URL ?? "";
            const res = await fetch(`${baseUrl}/api/v1/pilots/${MOCK_USER_ID}/telemetry/upload`, {
                method: "POST",
                body: formData,
                headers: { "X-Telegram-Id": String(MOCK_USER_ID) },
            });

            const data = await res.json();
            if (res.ok && data.ok) {
                toast.success(data.message);
                setUploadedHours(data.total_hours);
                setFile(null);
            } else {
                toast.error(data.error || "Ошибка при обработке лога");
            }
        } catch {
            toast.error("Ошибка соединения с сервером Горизонта");
        } finally {
            setLoading(false);
            if (fileInputRef.current) fileInputRef.current.value = "";
        }
    };

    return (
        <div className="max-w-4xl mx-auto px-4 py-8">
            <div className="mb-4">
                <h1 className="text-3xl font-black text-white flex items-center gap-3">
                    <CloudRain className="w-8 h-8 text-blue-400" />
                    Управление Полетами
                </h1>
                <p className="text-gray-400 mt-2">
                    Подтверждайте часы налёта логами DJI и запрашивайте воздушное пространство (ИВП) у ОрВД.
                </p>
            </div>

            <div className="flex border-b border-white/10 mb-8 border-khokhloma-gold/30">
                <button 
                  onClick={() => setActiveTab("logs")}
                  className={`px-6 py-3 font-bold text-sm tracking-wide ${activeTab === 'logs' ? 'text-khokhloma-gold border-b-2 border-khokhloma-gold' : 'text-gray-400 hover:text-white'}`}
                >
                    ЗАГРУЗКА ЛОГОВ DJI
                </button>
                <button 
                  onClick={() => setActiveTab("orvd")}
                  className={`px-6 py-3 font-bold text-sm tracking-wide ${activeTab === 'orvd' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400 hover:text-white'}`}
                >
                    РАЗРЕШЕНИЕ ИВП (РОСАВИАЦИЯ)
                </button>
            </div>

            {activeTab === "logs" && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4">
                
                {/* Левая панель - Drag and drop */}
                <div className="md:col-span-2">
                    <div 
                        className={`border-2 border-dashed rounded-3xl p-10 flex flex-col items-center justify-center transition-all bg-[#0A0A0B] min-h-[400px]
                        ${isDragging ? 'border-khokhloma-gold bg-khokhloma-gold/5 scale-[1.02]' : 'border-white/20 hover:border-white/40'}`}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        onClick={() => !file && fileInputRef.current?.click()}
                    >
                        {loading ? (
                            <div className="flex flex-col items-center">
                                <DroneLoader text="Анализ телеметрии нейросетью..." subtext="Читаем контрольные суммы и полетное время" color="gold" size="lg" />
                            </div>
                        ) : file ? (
                            <div className="flex flex-col items-center w-full">
                                <div className="w-20 h-20 bg-blue-500/10 rounded-2xl flex flex-col items-center justify-center mb-4 border border-blue-500/30">
                                    <FileText className="w-10 h-10 text-blue-400" />
                                </div>
                                <h3 className="text-xl font-bold text-white text-center break-all w-full mb-1">{file.name}</h3>
                                <p className="text-gray-500 text-sm mb-8">{(file.size / 1024 / 1024).toFixed(2)} MB • TXT Data Log</p>
                                
                                <div className="flex gap-4">
                                    <button 
                                        onClick={(e) => { e.stopPropagation(); setFile(null); }}
                                        className="px-6 py-3 rounded-xl bg-gray-800 hover:bg-gray-700 text-white font-medium transition-colors"
                                    >
                                        Отмена
                                    </button>
                                    <button 
                                        onClick={(e) => { e.stopPropagation(); handleUpload(); }}
                                        className="px-6 py-3 rounded-xl bg-khokhloma-gold hover:bg-yellow-600 text-black font-black uppercase tracking-wider transition-colors shadow-xl shadow-khokhloma-gold/20 flex items-center gap-2"
                                    >
                                        <UploadCloud className="w-5 h-5" /> Загрузить в Облако
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <>
                                <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mb-4 border border-white/10 group-hover:bg-white/10 transition-colors">
                                    <UploadCloud className="w-10 h-10 text-gray-400 group-hover:text-white" />
                                </div>
                                <h3 className="text-xl font-bold text-white mb-2">Перетащите лог-файл сюда</h3>
                                <p className="text-gray-500 mb-6 text-center max-w-sm">Или нажмите на область, чтобы выбрать файл .TXT из памяти устройства (до 50 МБ).</p>
                                <button className="px-6 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white font-medium transition-colors pointer-events-none">
                                    Выбрать Файл
                                </button>
                            </>
                        )}
                        <input 
                            type="file" 
                            ref={fileInputRef} 
                            onChange={handleFileChange} 
                            className="hidden" 
                            accept=".txt,.csv"
                        />
                    </div>
                </div>

                {/* Правая панель - Инструкции и Статус */}
                <div className="space-y-6">
                    <div className="bg-gradient-to-br from-[#121214] to-[#1A1B1F] border border-white/10 rounded-3xl p-6 relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-khokhloma-gold/10 rounded-full blur-3xl" />
                        
                        <h3 className="text-lg font-bold text-white mb-4 relative z-10 flex items-center gap-2">
                            <CheckCircle2 className="w-5 h-5 text-emerald-400" /> Верификация
                        </h3>
                        
                        {uploadedHours !== null ? (
                            <div className="relative z-10 bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4 text-center">
                                <p className="text-sm text-gray-300 font-bold uppercase mb-1">Суммарный налет</p>
                                <p className="text-4xl font-black text-emerald-400">{uploadedHours} ч</p>
                                <p className="text-xs text-emerald-500/70 mt-2">Полностью подтверждено</p>
                            </div>
                        ) : (
                            <div className="relative z-10 text-gray-400 text-sm space-y-3">
                                <p>Загрузка логов — единственный способ получить значок <strong className="text-khokhloma-gold">"Профи"</strong>.</p>
                                <ul className="list-disc pl-4 space-y-1">
                                    <li>Анализ крипто-подписи</li>
                                    <li>Защита от накруток времени</li>
                                    <li>GPS/GLONASS валидация треков</li>
                                </ul>
                            </div>
                        )}
                    </div>

                    {/* Phase 28: Отряд Резерва МЧС */}
                    <div className="bg-red-500/10 border border-red-500/30 rounded-3xl p-6 relative overflow-hidden flex flex-col gap-4">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-red-500/10 rounded-full blur-3xl pointer-events-none" />
                        <h3 className="text-lg font-bold text-red-400 relative z-10 flex items-center gap-2">
                             МЧС / Отряд Резерва
                        </h3>
                        <p className="text-xs text-gray-300 relative z-10">
                            Активируйте, если готовы выехать со своим БПЛА на поисково-спасательные операции (ПСО) или ликвидацию ЧС в Вашем регионе.
                        </p>
                        <button 
                            onClick={async () => {
                                // Phase 28 Action
                                const req = { telegram_id: MOCK_USER_ID, is_emergency_volunteer: true, emergency_region: "Россия / Беларусь" };
                                try {
                                    await api.post("/pilot/volunteer", req);
                                    toast.success("Вы добавлены в резерв МЧС! Оперативный штаб свяжется при ЧС.");
                                } catch { toast.error("Ошибка сети"); }
                            }}
                            className="relative z-10 w-full py-3 bg-red-500/20 hover:bg-red-500/40 border border-red-500/50 text-red-200 font-bold rounded-xl transition-all flex justify-center items-center gap-2"
                        >
                            Вступить в Отряд Спасения
                        </button>
                    </div>                    <div className="bg-blue-500/5 border border-blue-500/20 rounded-3xl p-6 flex flex-col gap-3">
                        <div className="flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
                            <div className="text-sm">
                                <h4 className="font-bold text-blue-300 mb-1">Где найти лог?</h4>
                                <p className="text-gray-400">
                                    В пульте DJI RC или на смартфоне перейдите во внутреннюю память: 
                                    <code className="block bg-black/50 px-2 py-1 rounded text-xs text-gray-300 mt-2 border border-white/10 text-wrap break-all">
                                        Android/data/dji.go.v5/files/FlightRecord
                                    </code>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
            )}

            {/* ВКЛАДКА ИВП ОРВД */}
            {activeTab === "orvd" && (
                <div className="bg-[#0A0A0B] border border-blue-500/20 rounded-3xl p-8 animate-in fade-in slide-in-from-bottom-4">
                    <h2 className="text-2xl font-bold text-white mb-6">Генератор Заявок на Полет (СППИ)</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm text-gray-400 block mb-1">Широта (N)</label>
                                    <input type="number" step="0.0001" value={orvdForm.lat} onChange={e => setOrvdForm({...orvdForm, lat: parseFloat(e.target.value)})} className="w-full bg-[#18181b] border border-white/10 text-white p-3 rounded-lg" />
                                </div>
                                <div>
                                    <label className="text-sm text-gray-400 block mb-1">Долгота (E)</label>
                                    <input type="number" step="0.0001" value={orvdForm.lng} onChange={e => setOrvdForm({...orvdForm, lng: parseFloat(e.target.value)})} className="w-full bg-[#18181b] border border-white/10 text-white p-3 rounded-lg" />
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm text-gray-400 block mb-1">Радиус (м)</label>
                                    <input type="number" value={orvdForm.radius} onChange={e => setOrvdForm({...orvdForm, radius: parseInt(e.target.value)})} className="w-full bg-[#18181b] border border-white/10 text-white p-3 rounded-lg" />
                                </div>
                                <div>
                                    <label className="text-sm text-gray-400 block mb-1">Высота до (м)</label>
                                    <input type="number" value={orvdForm.height} onChange={e => setOrvdForm({...orvdForm, height: parseInt(e.target.value)})} className="w-full bg-[#18181b] border border-white/10 text-white p-3 rounded-lg" />
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-sm text-gray-400 block mb-1">Начало (UTC)</label>
                                    <input type="datetime-local" value={orvdForm.start} onChange={e => setOrvdForm({...orvdForm, start: e.target.value})} className="w-full bg-[#18181b] border border-white/10 text-gray-300 p-3 rounded-lg" />
                                </div>
                                <div>
                                    <label className="text-sm text-gray-400 block mb-1">Окончание (UTC)</label>
                                    <input type="datetime-local" value={orvdForm.end} onChange={e => setOrvdForm({...orvdForm, end: e.target.value})} className="w-full bg-[#18181b] border border-white/10 text-gray-300 p-3 rounded-lg" />
                                </div>
                            </div>
                            <div>
                                <label className="text-sm text-gray-400 block mb-1">Модель БВС</label>
                                <input type="text" value={orvdForm.model} onChange={e => setOrvdForm({...orvdForm, model: e.target.value})} className="w-full bg-[#18181b] border border-white/10 text-white p-3 rounded-lg" />
                            </div>
                            <button
                                onClick={handleGenerateOrvd}
                                disabled={isGenerating}
                                className="w-full py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl mt-4 flex items-center justify-center gap-2"
                            >
                                {isGenerating ? <Loader2 className="w-5 h-5 animate-spin" /> : <FileText className="w-5 h-5" />}
                                Сгенерировать Формализованную Заявку
                            </button>
                        </div>

                        <div className="bg-[#121214] border border-white/5 rounded-2xl p-6 flex flex-col">
                            <h3 className="text-lg font-bold text-gray-300 mb-4 flex items-center gap-2">
                                <AlertCircle className="w-5 h-5 text-gray-500" />
                                Ваш План Полета (ТШС)
                            </h3>
                            {orvdResult ? (
                                <div className="space-y-4 flex-1 flex flex-col">
                                    <textarea 
                                        readOnly 
                                        value={orvdResult}
                                        className="w-full flex-1 min-h-[150px] font-mono text-sm bg-black/50 border border-blue-500/30 text-blue-400 p-4 rounded-xl resize-none outline-none"
                                    />
                                    <p className="text-xs text-gray-500 text-center">
                                        Скопируйте этот текст и отправьте в СППИ Росавиации. Копия отправлена в Telegram.
                                    </p>
                                </div>
                            ) : (
                                <div className="flex-1 flex items-center justify-center text-gray-600 italic">
                                    Заполните параметры и нажмите генерацию...
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

