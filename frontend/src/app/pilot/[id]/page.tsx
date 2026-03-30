"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { ShieldCheck, Award, Clock, Star, MapPin, Loader2, Building2, User } from "lucide-react";
import { toast } from "react-hot-toast";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

interface Certificate {
    type: string;
    document: string;
    verified: boolean;
    date: string;
}

interface PilotProfile {
    id: number;
    name: string;
    username: string | null;
    company_name: string | null;
    is_gosuslugi_verified: boolean;
    verified_flight_hours: number;
    certificates: Certificate[];
}

export default function PilotProfilePage() {
    const params = useParams();
    const telegram_id = params.id;
    
    const [profile, setProfile] = useState<PilotProfile | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (telegram_id) fetchProfile();
    }, [telegram_id]);

    const fetchProfile = async () => {
        try {
            const res = await fetch(`${API_BASE}/api/v1/pilots/${telegram_id}`);
            if (res.ok) {
                const data = await res.json();
                setProfile(data.pilot);
            } else {
                toast.error("Пилот не найден");
            }
        } catch {
            toast.error("Ошибка при подключении к серверу");
        } finally {
            setLoading(false);
        }
    };

    const handleGosuslugiVerification = async () => {
        // Эмуляция входа через ЕСИА (Госуслуги) для тестов MVP
        const id = Number(telegram_id);
        if (!id) return;
        
        try {
            const res = await fetch(`${API_BASE}/api/v1/auth/gosuslugi_login?telegram_id=${id}`, {
                method: "POST"
            });
            const data = await res.json();
            if (data.ok) {
                toast.success(data.message);
                fetchProfile(); // refresh data
            } else {
                toast.error(data.error);
            }
        } catch {
            toast.error("Сбой интеграции с Госуслугами");
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-[70vh]">
                <Loader2 className="w-12 h-12 animate-spin text-khokhloma-gold" />
            </div>
        );
    }

    if (!profile) return <div className="text-center text-white py-20 text-xl font-bold">Профиль скрыт или не существует</div>;

    return (
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 transition-all">
            {/* Карточка профиля */}
            <div className="relative overflow-hidden bg-gradient-to-br from-[#121214] to-[#0A0A0B] border border-white/10 rounded-3xl p-8 mb-8">
                {/* Visual Flair */}
                {profile.is_gosuslugi_verified && (
                    <div className="absolute top-0 right-0 w-[400px] h-full bg-pattern-khokhloma opacity-5 pointer-events-none" />
                )}
                
                <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center gap-6">
                    {/* Аватар (Заглушка) */}
                    <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 border border-white/10 flex items-center justify-center shadow-2xl shrink-0">
                        <User className="w-10 h-10 text-white" />
                    </div>

                    <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-3">
                            <h1 className="text-3xl font-black text-white">{profile.name}</h1>
                            {profile.is_gosuslugi_verified && (
                                <span className="flex items-center gap-1 px-3 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/30 rounded-full text-xs font-bold uppercase tracking-wider tooltip" title="Подтвержденная учетная запись ЕСИА">
                                    <ShieldCheck className="w-4 h-4" /> Госуслуги
                                </span>
                            )}
                        </div>
                        
                        <p className="text-gray-400 font-medium">
                            {profile.username ? `@${profile.username}` : "Скрытый профиль"}
                        </p>
                        
                        {profile.company_name && (
                            <p className="text-sm flex items-center gap-2 text-khokhloma-gold font-bold">
                                <Building2 className="w-4 h-4" /> B2B Аккаунт: {profile.company_name}
                            </p>
                        )}
                    </div>
                    
                    <div className="flex flex-col gap-3 md:items-end w-full md:w-auto mt-4 md:mt-0">
                         {/* Stats Box */}
                         <div className="bg-[#1A1A1E] rounded-xl p-4 flex gap-6 shrink-0 border border-white/5">
                            <div className="text-center">
                                <p className="text-gray-400 text-xs font-bold uppercase mb-1 flex items-center gap-1 justify-center"><Star className="w-3 h-3 text-yellow-400"/> Рейтинг</p>
                                <p className="text-xl font-bold text-white">4.9/5</p>
                            </div>
                            <div className="w-px bg-white/10"></div>
                            <div className="text-center">
                                <p className="text-gray-400 text-xs font-bold uppercase mb-1 flex items-center gap-1 justify-center"><Clock className="w-3 h-3 text-emerald-400"/> Налёт (Часы)</p>
                                <p className="text-xl font-bold text-white">{profile.verified_flight_hours > 0 ? profile.verified_flight_hours : "—"}</p>
                            </div>
                         </div>
                    </div>
                </div>
            </div>

            {/* Верификация и документы */}
            <div className="space-y-6">
                <h2 className="text-2xl font-black text-white mb-4">Регалии и Сертификаты</h2>
                
                {/* Если нет Госуслуг - предлагаем пройти */}
                {!profile.is_gosuslugi_verified && (
                    <div className="bg-blue-500/5 border border-blue-500/20 rounded-2xl p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
                        <div>
                            <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-1">
                                <ShieldCheck className="w-5 h-5 text-blue-400" /> Подтвердите личность
                            </h3>
                            <p className="text-sm text-gray-400">Свяжите профиль с ЕСИА Госуслуги, чтобы получать крупные Госконтракты.</p>
                        </div>
                        <button 
                            onClick={handleGosuslugiVerification}
                            className="shrink-0 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl transition-all shadow-lg"
                        >
                            Войти через ЕСИА
                        </button>
                    </div>
                )}

                {/* Grid Сертификатов */}
                {profile.certificates.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {profile.certificates.map((cert, idx) => (
                            <div key={idx} className="bg-[#121214] border border-white/10 rounded-2xl p-6 hover:border-khokhloma-gold/30 transition-all group relative overflow-hidden">
                                {cert.verified && <div className="absolute top-0 right-0 w-20 h-20 bg-blue-500/10 rounded-full filter blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />}
                                
                                <div className="flex items-start justify-between mb-4">
                                    <div className="w-12 h-12 bg-gray-800 rounded-lg flex items-center justify-center">
                                        <Award className={`w-6 h-6 ${cert.verified ? "text-khokhloma-gold" : "text-gray-400"}`} />
                                    </div>
                                    {cert.verified && (
                                        <span className="bg-emerald-500/20 text-emerald-400 text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-md border border-emerald-500/30">
                                            Проверено
                                        </span>
                                    )}
                                </div>
                                
                                <h4 className="text-sm font-bold text-white mb-1 line-clamp-2">{cert.type}</h4>
                                <p className="text-xs text-gray-500 font-mono">{cert.document}</p>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-12 border border-dashed border-white/10 rounded-2xl">
                        <p className="text-gray-500">Пилот пока не загрузил данные об обучении.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
