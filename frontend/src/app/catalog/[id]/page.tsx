import Link from "next/link";
import { ArrowLeft, MapPin, User, Tag, Calendar, ShieldCheck, FileText } from "lucide-react";

export const revalidate = 60;

async function getListing(id: string) {
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/v1/public/listings/${id}`, {
      next: { revalidate: 60 }
    });
    if (!res.ok) return null;
    const data = await res.json();
    return data.listing;
  } catch (err) {
    console.error("Fetch error:", err);
    return null;
  }
}

export default async function ListingDetail({ params }: { params: { id: string } }) {
  const listing = await getListing(params.id);

  if (!listing) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-24 text-center">
        <h1 className="text-3xl font-bold text-white mb-4">Объявление не найдено</h1>
        <p className="text-gray-400 mb-8">Возможно оно было удалено или снято с публикации.</p>
        <Link href="/catalog" className="text-blue-400 hover:text-blue-300">
          &larr; Вернуться в каталог
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Link href="/catalog" className="inline-flex items-center text-sm font-medium text-gray-400 hover:text-white mb-8 transition-colors">
        <ArrowLeft className="w-4 h-4 mr-2" /> Назад в каталог
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Main Content (Left) */}
        <div className="lg:col-span-2 space-y-8">
          {/* Main Image Slider Placeholder */}
          <div className="aspect-w-16 aspect-h-9 bg-black/50 rounded-3xl overflow-hidden border border-white/10 relative group">
            <div className="absolute inset-0 flex items-center justify-center text-gray-700 bg-[#0A0A0B]">
              <svg className="w-20 h-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            {listing.is_sponsored && (
              <div className="absolute top-4 left-4 bg-gradient-to-r from-amber-500 to-orange-500 text-xs font-bold px-3 py-1.5 rounded-lg text-white shadow-lg uppercase tracking-wider">
                PRO Размещение
              </div>
            )}
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-2 mb-4">
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-blue-500/20 text-blue-400 border border-blue-500/30">
                Категория: {listing.category_id}
              </span>
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-white/5 text-gray-400 border border-white/10">
                ID: {listing.id}
              </span>
            </div>
            
            <h1 className="text-3xl md:text-4xl font-extrabold text-white mb-6 leading-tight">
              {listing.title}
            </h1>
            
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6 mb-8">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5 text-gray-400" />
                Описание
              </h3>
              <p className="text-gray-300 whitespace-pre-line leading-relaxed">
                {listing.description}
              </p>
            </div>
          </div>
        </div>

        {/* Sidebar Info (Right) */}
        <div className="lg:col-span-1">
          <div className="bg-[#0A0A0B] border border-white/10 rounded-3xl p-6 sticky top-24 shadow-2xl">
            
            <div className="mb-6">
              <p className="text-sm text-gray-400 font-medium uppercase tracking-wider mb-1">Стоимость</p>
              <div className="text-3xl font-bold font-mono text-white break-words">
                {listing.price}
              </div>
            </div>

            <div className="space-y-4 mb-8">
              <div className="flex items-start gap-3">
                <User className="w-5 h-5 text-gray-500 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-400">Владелец</p>
                  <p className="text-white font-medium">{listing.seller_name}</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-gray-500 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-400">Локация</p>
                  <p className="text-white font-medium">{listing.city}</p>
                  {listing.address && <p className="text-xs text-gray-500 mt-1">{listing.address}</p>}
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Calendar className="w-5 h-5 text-gray-500 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-400">Опубликовано</p>
                  <p className="text-white font-medium">{new Date(listing.created_at).toLocaleDateString()}</p>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="space-y-3">
              <Link href={`https://t.me/SkyRentAdminBot?start=contact_${listing.seller_id}`} target="_blank" className="w-full flex justify-center py-3.5 px-4 border border-transparent rounded-xl shadow-sm shadow-blue-500/20 text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none transition-all hover:-translate-y-0.5">
                Связаться с владельцем
              </Link>
              <Link href={`/dashboard/docs?type=contract&listing_id=${listing.id}`} className="w-full flex justify-center py-3.5 px-4 border border-white/10 rounded-xl text-sm font-bold text-white bg-white/5 hover:bg-white/10 focus:outline-none transition-all">
                Сформировать договор
              </Link>
            </div>

            <div className="mt-6 pt-6 border-t border-white/10">
              <div className="flex items-center gap-3 text-sm text-emerald-400 bg-emerald-500/10 p-4 rounded-xl border border-emerald-500/20">
                <ShieldCheck className="w-6 h-6 shrink-0" />
                <p>Безопасная сделка доступна для пользователей с премиум-подпиской.</p>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}
