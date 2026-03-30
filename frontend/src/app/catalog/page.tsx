import Link from "next/link";
import CatalogFilters from "./CatalogFilters";
import DroneRoiLadder from "./DroneRoiLadder";

export const revalidate = 0; // Dynamic component due to searchParams

async function getListings(searchParams: { [key: string]: string | string[] | undefined }) {
  const url = new URL("http://127.0.0.1:8000/api/v1/public/listings");
  
  if (searchParams.category_id) url.searchParams.append("category_id", searchParams.category_id as string);
  if (searchParams.city) url.searchParams.append("city", searchParams.city as string);
  if (searchParams.q) url.searchParams.append("q", searchParams.q as string);

  try {
    const res = await fetch(url.toString(), { cache: "no-store" });
    if (!res.ok) {
      console.error("Failed to fetch listings:", res.status);
      return [];
    }
    const data = await res.json();
    return data.listings || [];
  } catch (err) {
    console.error("Fetch error:", err);
    return [];
  }
}

export default async function Catalog({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined };
}) {
  const listings = await getListings(searchParams);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col md:flex-row justify-between items-baseline mb-8 border-b border-white/5 pb-4 relative">
        <div className="absolute top-0 right-0 w-32 h-32 bg-khokhloma-gold rounded-full mix-blend-screen filter blur-[100px] opacity-10 pointer-events-none"></div>
        <div>
          <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-khokhloma-gold to-yellow-600 tracking-tight uppercase">Маркетплейс</h1>
          <p className="text-gray-400 mt-2">Единая витрина Национальной Экосистемы БАС</p>
        </div>
        <p className="text-gray-300 mt-4 md:mt-0 bg-khokhloma-gold/10 px-4 py-1.5 rounded-full text-sm font-bold border border-khokhloma-gold/30 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-khokhloma-gold animate-pulse"></span>
          Найдено: {listings.length}
        </p>
      </div>

      <DroneRoiLadder />

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Filters Sidebar */}
        <div className="w-full lg:w-64 shrink-0">
          <CatalogFilters currentParams={searchParams} />
        </div>

        {/* Catalog Grid */}
        <div className="flex-1">
          {listings.length === 0 ? (
            <div className="text-center py-24 bg-white/5 rounded-2xl border border-white/10 flex flex-col items-center justify-center">
              <svg className="w-16 h-16 text-gray-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-xl text-gray-400 font-medium">По вашему запросу ничего не найдено.</p>
              <p className="text-gray-500 mt-2">Попробуйте изменить параметры фильтра.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-6">
              {listings.map((lst: any) => (
                <Link href={`/catalog/${lst.id}`} key={lst.id} className="bg-[#111111]/90 border border-white/5 rounded-2xl overflow-hidden hover:bg-white/5 relative group hover:-translate-y-1 transition-all hover:shadow-[0_10px_30px_rgba(245,176,65,0.1)] hover:border-khokhloma-gold/30">
                  <div className="absolute inset-0 bg-gradient-to-br from-khokhloma-gold/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <div className="aspect-w-16 aspect-h-10 bg-black/50 relative overflow-hidden">
                    <div className="absolute inset-0 flex items-center justify-center text-gray-600 bg-gray-900 group-hover:scale-105 transition-transform duration-500">
                      <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                    </div>
                    {lst.is_sponsored && (
                      <div className="absolute top-3 left-3 bg-gradient-to-r from-amber-500 to-orange-500 text-[10px] uppercase tracking-wider font-bold px-2.5 py-1 rounded-md text-white shadow-lg flex items-center gap-1">
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>
                        PRO
                      </div>
                    )}
                    <div className="absolute bottom-3 right-3 bg-black/70 backdrop-blur-md text-xs font-semibold px-2 py-1 rounded-md border border-white/20">
                      ID: {lst.id}
                    </div>
                  </div>
                  <div className="p-5 flex-1 flex flex-col relative z-10">
                    <div className="flex justify-between items-start gap-2 mb-2">
                      <h3 className="font-bold text-lg text-white line-clamp-2 leading-tight group-hover:text-khokhloma-gold transition-colors">{lst.title}</h3>
                    </div>
                    <div className="text-sm text-gray-400 mb-4 space-y-2 mt-2">
                      <p className="flex items-center gap-2">
                        <svg className="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                        {lst.city || "Город не указан"}
                      </p>
                      <p className="flex items-center gap-2">
                        <svg className="w-4 h-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                        {lst.seller_name || "Пользователь"}
                      </p>
                    </div>
                    <div className="mt-auto pt-4 border-t border-white/5 flex items-center justify-between">
                      <div className="text-xl font-bold font-mono text-khokhloma-gold truncate drop-shadow-md">{lst.price}</div>
                      <div className="w-8 h-8 rounded-full bg-khokhloma-gold/10 flex items-center justify-center group-hover:bg-khokhloma-gold/30 border border-khokhloma-gold/20 transition-colors">
                        <svg className="w-4 h-4 text-khokhloma-gold transform group-hover:translate-x-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
