/**
 * Горизонт API Client — единая точка для всех запросов к /api/v1/*
 * Авторизация: X-Telegram-Id берётся из localStorage (skyrent_user)
 *
 * Использование:
 *   import { api } from "@/lib/api";
 *   const trackers = await api.get("/trackers");
 *   const booking  = await api.post("/droneport-bookings", payload);
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";
const API_V1   = `${API_BASE}/api/v1`;

// ─── Типы ────────────────────────────────────────────────────────────────────

export interface ApiError {
  detail: string;
  status: number;
}

// Трекеры
export interface Tracker {
  id: number;
  tracker_id: string;
  nickname: string;
  drone_model: string;
  serial_number: string;
  orvd_visible: boolean;
  is_active: boolean;
  last_lat: number | null;
  last_lng: number | null;
  last_battery_pct: number | null;
  last_altitude_m: number | null;
  last_speed_kmh: number | null;
  last_seen_at: string | null;
  registered_at: string;
}

// Бронирования дронопортов
export interface DroneportBooking {
  id: number;
  port_id: string;
  port_name: string;
  slot_from: string;
  slot_to: string;
  status: string;
  qr_token: string | null;
  total_rub: number | null;
  created_at: string;
}

// Датасеты
export interface Dataset {
  id: number;
  flight_id: string;
  area_name: string;
  tags: string;
  size_gb: number;
  price_usdt: number;
  status: string;
  buyer_count: number;
  pii_sanitized: boolean;
  created_at: string;
}

// Записи на курсы
export interface CourseEnrollment {
  id: number;
  course_id: number;
  course_title: string;
  progress_pct: number;
  is_completed: boolean;
  certificate_issued: boolean;
  cert_number: string | null;
  enrolled_at: string;
}

// Заявки на лизинг
export interface LeasingApplication {
  id: number;
  company_name: string;
  drone_model: string;
  requested_amount_rub: number;
  status: string;
  created_at: string;
}

// Патенты
export interface PatentApplication {
  id: number;
  title: string;
  ipc_codes: string;
  status: string;
  progress_pct: number;
  is_secret: boolean;
  fips_id: string | null;
  created_at: string;
}

// Профиль пилота
export interface Profile {
  telegram_id: number;
  full_name: string | null;
  username: string | null;
  user_type: string;
  verified_flight_hours: number;
  is_emergency_volunteer: boolean;
  inn: string | null;
  company_name: string | null;
  referral_bonus: number;
  is_admin: boolean;
  is_moderator: boolean;
}

export interface PilotStats {
  trackers: number;
  active_bookings: number;
  enrollments: number;
  certificates: number;
  datasets_listed: number;
  patents: number;
  leasing_applications: number;
  flight_hours: number;
  referral_bonus: number;
  volunteer_rescues: number;
}

// ─── Утилиты ─────────────────────────────────────────────────────────────────

/** Получаем Telegram ID из localStorage */
function getTelegramId(): string | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem("skyrent_user");
    if (!raw) return null;
    const user = JSON.parse(raw);
    return String(user.telegram_id ?? user.id ?? "");
  } catch {
    return null;
  }
}

/** Базовые заголовки для всех запросов */
function headers(extra?: Record<string, string>): Record<string, string> {
  const tgId = getTelegramId();
  return {
    "Content-Type": "application/json",
    ...(tgId ? { "X-Telegram-Id": tgId } : {}),
    ...extra,
  };
}

/** Обёртка над fetch с обработкой ошибок */
async function request<T>(
  method: "GET" | "POST" | "PATCH" | "DELETE",
  path: string,
  body?: unknown
): Promise<T> {
  const res = await fetch(`${API_V1}${path}`, {
    method,
    headers: headers(),
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      detail = err.detail ?? detail;
    } catch {}
    throw { detail, status: res.status } satisfies ApiError;
  }

  // DELETE возвращает 204 без тела
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ─── API-клиент ───────────────────────────────────────────────────────────────

export const api = {
  get:    <T>(path: string)               => request<T>("GET",    path),
  post:   <T>(path: string, body: unknown) => request<T>("POST",   path, body),
  patch:  <T>(path: string, body?: unknown)=> request<T>("PATCH",  path, body),
  delete: <T>(path: string)               => request<T>("DELETE",  path),
} as const;

// ─── Типизированные хелперы ───────────────────────────────────────────────────

export const trackerApi = {
  list:     ()                                => api.get<Tracker[]>("/trackers"),
  register: (data: { nickname: string; drone_model: string; serial_number: string }) =>
                                                 api.post<Tracker>("/trackers", data),
  delete:   (trackerId: string)               => api.delete<void>(`/trackers/${trackerId}`),
};

export const droneportApi = {
  list:   ()              => api.get<DroneportBooking[]>("/droneport-bookings"),
  book:   (data: {
    port_id: string; port_name: string; tracker_id?: string;
    slot_from: string; slot_to: string; tariff_per_h: number;
  })                      => api.post<DroneportBooking>("/droneport-bookings", data),
  cancel: (id: number)    => api.patch<DroneportBooking>(`/droneport-bookings/${id}/cancel`),
};

export const datasetApi = {
  list:    ()            => api.get<Dataset[]>("/datasets"),
  create:  (data: {
    flight_id: string; area_name: string; tags: string;
    size_gb: number; resolution_cm?: number; has_lidar?: boolean; has_thermal?: boolean;
  })                     => api.post<Dataset>("/datasets", data),
  publish: (id: number)  => api.patch<Dataset>(`/datasets/${id}/publish`),
};

export const academyApi = {
  enrollments: ()          => api.get<CourseEnrollment[]>("/academy/enrollments"),
  enroll:      (course_id: number, course_title: string) =>
                              api.post<CourseEnrollment>("/academy/enroll", { course_id, course_title }),
  complete:    (id: number) => api.patch<CourseEnrollment>(`/academy/enrollments/${id}/complete`),
};

export const leasingApi = {
  list:   ()      => api.get<LeasingApplication[]>("/leasing"),
  create: (data: {
    company_name: string; inn: string; contact_email: string;
    contact_phone?: string; drone_model: string;
    tender_guarantee_id?: string; requested_amount_rub: number;
  })              => api.post<LeasingApplication>("/leasing", data),
};

export const patentApi = {
  list:   ()           => api.get<PatentApplication[]>("/patents"),
  submit: (data: {
    title: string; ipc_codes: string; abstract: string; claims: string;
    author_name?: string; organization?: string; inn?: string; is_secret?: boolean;
  })                   => api.post<PatentApplication>("/patents", data),
  file:   (id: number) => api.post<PatentApplication>(`/patents/${id}/file`, {}),
};

export const profileApi = {
  me:    ()  => api.get<Profile>("/me"),
  stats: ()  => api.get<PilotStats>("/me/stats"),
};
