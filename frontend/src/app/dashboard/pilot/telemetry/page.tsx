"use client";

import { useState, useRef } from "react";
import { CloudRain, UploadCloud, CheckCircle2, AlertCircle, FileText, Loader2 } from "lucide-react";
import { toast } from "react-hot-toast";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export default function TelemetryUploadPage() {
    const [isDragging, setIsDragging] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);
    const [uploadedHours, setUploadedHours] = useState<number | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // В реальном приложении ID берется из локального стейта/сессии
    const MOCK_USER_ID = 0; 

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
            const res = await fetch(`${API_BASE}/api/v1/pilots/${MOCK_USER_ID}/telemetry/upload`, {
                method: "POST",
                body: formData,
            });

            const data = await res.json();
            if (res.ok && data.ok) {
                toast.success(data.message);
                setUploadedHours(data.total_hours);
                setFile(null);
            } else {
                toast.error(data.error || "Ошибка при обработке лога");
            }
        } catch (error) {
            toast.error("Ошибка соединения с сервером Горизонта");
        } finally {
            setLoading(false);
            if (fileInputRef.current) fileInputRef.current.value = "";
        }
    };

    return (
        <div className="max-w-4xl mx-auto px-4 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-black text-white flex items-center gap-3">
                    <CloudRain className="w-8 h-8 text-blue-400" />
                    Облачная Телеметрия ГОРИЗОНТ
                </h1>
                <p className="text-gray-400 mt-2">
                    Подтвердите свои часы налёта для доступа к высокобюджетным Государственным Тендерам (B2G). 
                    Мы принимаем официальные полетные логи из приложений DJI Fly, DJI Pilot и Autel Explorer.
                </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
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
                                <Loader2 className="w-16 h-16 text-khokhloma-gold animate-spin mb-4" />
                                <p className="text-white font-bold text-lg animate-pulse">Анализ телеметрии нейросетью...</p>
                                <p className="text-gray-500 text-sm mt-2">Читаем контрольные суммы и полетное время</p>
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

                    <div className="bg-blue-500/5 border border-blue-500/20 rounded-3xl p-6 flex flex-col gap-3">
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
        </div>
    );
}

