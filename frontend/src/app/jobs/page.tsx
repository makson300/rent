import Link from "next/link";
import JobFilters from "./JobFilters";

export const revalidate = 0; // dynamic depending on searchParams

async function getJobs(searchParams: { [key: string]: string | string[] | undefined }) {
  const url = new URL("http://127.0.0.1:8000/api/v1/public/jobs");
  
  if (searchParams.city) url.searchParams.append("city", searchParams.city as string);
  if (searchParams.q) url.searchParams.append("q", searchParams.q as string);

  try {
    const res = await fetch(url.toString(), { cache: "no-store" });
    if (!res.ok) {
      console.error("Failed to fetch jobs:", res.status);
      return [];
    }
    const data = await res.json();
    return data.jobs || [];
  } catch (err) {
    console.error("Fetch error:", err);
    return [];
  }
}

export default async function Jobs({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined };
}) {
  const jobs = await getJobs(searchParams);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col md:flex-row justify-between items-baseline mb-8 border-b border-white/5 pb-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white">Биржа Услуг</h1>
          <p className="text-gray-400 mt-2">Заказы, фриланс и проектные работы для пилотов 🚁</p>
        </div>
        <p className="text-gray-400 mt-4 md:mt-0 bg-blue-500/10 px-3 py-1 rounded-full text-sm font-medium border border-blue-500/20 text-blue-400">
          Актуально заданий: {jobs.length}
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Filters Sidebar */}
        <div className="w-full lg:w-64 shrink-0">
          <JobFilters currentParams={searchParams} />
        </div>

        {/* Jobs Grid */}
        <div className="flex-1">
          {jobs.length === 0 ? (
            <div className="text-center py-24 bg-white/5 rounded-2xl border border-white/10 flex flex-col items-center justify-center">
              <svg className="w-16 h-16 text-gray-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <p className="text-xl text-gray-400">Нет открытых вакансий по вашим фильтрам.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
              {jobs.map((job: any) => (
                <div key={job.id} className="relative bg-white/5 border border-white/10 p-6 rounded-2xl hover:bg-white/10 transition-colors flex flex-col group hover:-translate-y-1 hover:shadow-xl hover:shadow-emerald-500/10 cursor-pointer">
                  <div className="mb-4">
                    <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold tracking-wide bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 uppercase">
                      {job.category}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-3 line-clamp-2 leading-snug group-hover:text-emerald-400 transition-colors">{job.title}</h3>
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
                  
                  <div className="flex items-end justify-between mt-auto pt-4 border-t border-white/5">
                    <div className="font-mono text-xl font-bold text-white">
                      {job.budget}
                    </div>
                    <button className="bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-xl text-sm font-medium shadow-lg shadow-emerald-500/20 transition-all opacity-0 group-hover:opacity-100 transform translate-y-2 group-hover:translate-y-0">
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
