import Link from "next/link";
import JobFilters from "./JobFilters";

export const revalidate = 0; // dynamic depending on searchParams

async function getJobs(searchParams: { [key: string]: string | string[] | undefined }) {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
  const url = new URL(`${baseUrl}/api/v1/public/jobs`);
  
  if (searchParams.city) url.searchParams.append("city", searchParams.city as string);
  if (searchParams.q) url.searchParams.append("q", searchParams.q as string);

  try {
    const res = await fetch(url.toString(), { cache: "no-store" });
    if (!res.ok) {
      console.error("Failed to fetch jobs:", res.status);
      return { data: [], error: `Ошибка сервера (Код ${res.status})` };
    }
    const data = await res.json();
    return { data: data.jobs || [], error: null };
  } catch (err: any) {
    console.error("Fetch error:", err);
    return { data: [], error: err.message || "Ошибка соединения с сервером (SSL или сеть)" };
  }
}

export default async function Jobs({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await searchParams;
  const { data: jobs, error } = await getJobs(params);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col md:flex-row justify-between items-baseline mb-8 border-b border-white/5 pb-4 relative">
        <div className="absolute top-0 right-0 w-32 h-32 bg-tricolor-blue rounded-full mix-blend-screen filter blur-[100px] opacity-10 pointer-events-none"></div>
        <div>
          <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-tricolor-blue tracking-tight uppercase">Биржа Работ и Тендеры</h1>
          <p className="text-gray-400 mt-2">Официальные заказы, государственные контракты и B2B услуги</p>
        </div>
        <p className="text-gray-300 mt-4 md:mt-0 bg-tricolor-blue/10 px-4 py-1.5 rounded-full text-sm font-bold border border-tricolor-blue/30 flex items-center gap-2 shadow-[0_0_15px_rgba(0,57,166,0.2)]">
          <span className={`w-2 h-2 rounded-full animate-pulse ${error ? "bg-red-500" : "bg-tricolor-blue"}`}></span>
          {error ? "Сервер недоступен" : `Актуально заданий: ${jobs.length}`}
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Filters Sidebar */}
        <div className="w-full lg:w-64 shrink-0">
          <JobFilters currentParams={searchParams} />
        </div>

        {/* Jobs Grid */}
        <div className="flex-1">
          {error ? (
            <div className="text-center py-24 bg-red-500/5 rounded-2xl border border-red-500/20 flex flex-col items-center justify-center">
              <svg className="w-16 h-16 text-red-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <h3 className="text-xl font-bold mb-2 text-white">Сервис временно недоступен</h3>
              <p className="text-gray-400 max-w-lg text-center">Не удалось загрузить биржу работ ({error}). Повторите попытку позже.</p>
            </div>
          ) : jobs.length === 0 ? (
            <div className="text-center py-24 bg-white/5 rounded-2xl border border-white/10 flex flex-col items-center justify-center">
              <svg className="w-16 h-16 text-gray-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <p className="text-xl text-gray-400">Нет открытых вакансий по вашим фильтрам.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
              {jobs.map((job: any) => (
                <div key={job.id} className="relative bg-[#111111]/90 border border-white/5 p-6 rounded-2xl hover:bg-white/5 transition-colors flex flex-col group hover:-translate-y-1 hover:shadow-xl hover:shadow-tricolor-blue/10 hover:border-tricolor-blue/30 cursor-pointer overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-tricolor-blue/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <div className="mb-4 relative z-10">
                    <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold tracking-wide bg-tricolor-blue/15 text-white border border-tricolor-blue/40 uppercase shadow-sm">
                      {job.category}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3 line-clamp-2 leading-snug group-hover:text-blue-200 transition-colors relative z-10">{job.title}</h3>
                  <p className="text-gray-400 text-sm mb-6 line-clamp-3 leading-relaxed flex-1">
                    {job.description}
                  </p>
                  <div className="flex flex-col gap-2 text-sm text-gray-500 mb-6">
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                      {job.city}
                    </div>
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
                      {job.employer_name}
                    </div>
                  </div>
                  
                  <div className="flex items-end justify-between mt-auto pt-4 border-t border-white/5 relative z-10">
                    <div className="font-mono text-2xl font-bold text-white drop-shadow-md">
                      {job.budget}
                    </div>
                    <button className="bg-gradient-to-r from-tricolor-blue to-blue-800 hover:from-blue-600 hover:to-blue-900 text-white px-5 py-2.5 rounded-xl text-sm font-bold shadow-lg shadow-tricolor-blue/30 transition-all opacity-0 group-hover:opacity-100 transform translate-y-2 group-hover:translate-y-0">
                      Откликнуться
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
