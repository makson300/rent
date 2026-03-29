/**
 * Бесполётные зоны РФ (Московский регион + крупные аэропорты).
 * Данные: центр зоны (lat, lng), радиус в метрах, название, тип ограничения.
 * Источник: публичные данные AIP Russia, НОТАМы.
 */

export interface NoFlyZone {
  id: string;
  name: string;
  lat: number;
  lng: number;
  radiusKm: number;        // радиус в километрах
  type: "airport" | "restricted" | "danger" | "prohibited";
  description: string;
}

export const NOFLY_ZONES: NoFlyZone[] = [
  // === Аэропорты Московского авиаузла ===
  {
    id: "svo",
    name: "Шереметьево (SVO)",
    lat: 55.9726,
    lng: 37.4146,
    radiusKm: 30,
    type: "airport",
    description: "CTR Шереметьево. Полёты БПЛА запрещены без согласования с ОрВД.",
  },
  {
    id: "dme",
    name: "Домодедово (DME)",
    lat: 55.4088,
    lng: 37.9063,
    radiusKm: 30,
    type: "airport",
    description: "CTR Домодедово. Полёты БПЛА запрещены без согласования.",
  },
  {
    id: "vko",
    name: "Внуково (VKO)",
    lat: 55.5915,
    lng: 37.2615,
    radiusKm: 30,
    type: "airport",
    description: "CTR Внуково. Полёты БПЛА запрещены без согласования.",
  },
  {
    id: "zhk",
    name: "Жуковский (ZIA)",
    lat: 55.5533,
    lng: 38.1501,
    radiusKm: 25,
    type: "airport",
    description: "CTR Жуковский / Раменское. Испытательный аэродром.",
  },
  // === Режимные объекты Москвы ===
  {
    id: "kremlin",
    name: "Кремль / Центр Москвы",
    lat: 55.7520,
    lng: 37.6175,
    radiusKm: 10,
    type: "prohibited",
    description: "Зона абсолютного запрета. БПЛА запрещены без исключений.",
  },
  // === Крупные аэропорты РФ ===
  {
    id: "led",
    name: "Пулково (LED)",
    lat: 59.8003,
    lng: 30.2625,
    radiusKm: 30,
    type: "airport",
    description: "CTR Пулково, Санкт-Петербург.",
  },
  {
    id: "svx",
    name: "Кольцово (SVX)",
    lat: 56.7431,
    lng: 60.8027,
    radiusKm: 25,
    type: "airport",
    description: "CTR Кольцово, Екатеринбург.",
  },
  {
    id: "kzn",
    name: "Казань (KZN)",
    lat: 55.6062,
    lng: 49.2787,
    radiusKm: 25,
    type: "airport",
    description: "CTR Казань.",
  },
  {
    id: "ovb",
    name: "Толмачёво (OVB)",
    lat: 55.0126,
    lng: 82.6507,
    radiusKm: 25,
    type: "airport",
    description: "CTR Толмачёво, Новосибирск.",
  },
  {
    id: "aer",
    name: "Адлер/Сочи (AER)",
    lat: 43.4499,
    lng: 39.9566,
    radiusKm: 25,
    type: "airport",
    description: "CTR Адлер-Сочи.",
  },
  {
    id: "kuf",
    name: "Курумоч (KUF)",
    lat: 53.5049,
    lng: 50.1643,
    radiusKm: 25,
    type: "airport",
    description: "CTR Курумоч, Самара.",
  },
  {
    id: "rov",
    name: "Платов (ROV)",
    lat: 47.4933,
    lng: 39.9244,
    radiusKm: 25,
    type: "airport",
    description: "CTR Платов, Ростов-на-Дону.",
  },
];
