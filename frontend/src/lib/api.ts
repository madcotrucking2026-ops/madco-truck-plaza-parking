import { clearToken, getToken } from "@/lib/auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
    cache: "no-store",
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    // Only a session that WAS authenticated and got rejected (expired/
    // invalid token) should bounce to /login — a bare 401 with no token to
    // begin with is a normal login failure or a public endpoint's own logic,
    // and must stay an in-place error the caller handles itself.
    if (res.status === 401 && token && typeof window !== "undefined") {
      clearToken();
      window.location.href = "/login";
    }
    throw new ApiError(body.detail ?? "Request failed", res.status);
  }

  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, data: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(data) }),
  patch: <T>(path: string, data: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(data) }),
};

export type AuthStatus = {
  needs_setup: boolean;
};

export type UserRead = {
  id: number;
  name: string;
  email: string;
  role: "admin" | "manager" | "attendant";
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  user: UserRead;
};

export type DashboardStats = {
  todays_revenue: number;
  todays_vehicles: number;
  active_daily_passes: number;
  active_weekly_passes: number;
  active_monthly_passes: number;
  expired_passes: number;
  expiring_today: number;
  expiring_tomorrow: number;
  companies_needing_follow_up: number;
  occupied_spaces: number;
  capacity: number;
  available_spaces: number;
  occupancy_pct: number;
  monthly_revenue: number;
  weekly_revenue: number;
};

export type ConversionLead = {
  company_id: number;
  company_name: string;
  phone: string | null;
  visits: number;
  total_spent: number;
  current_monthly_equivalent: number;
  suggested_monthly: number;
  tier: "hot" | "warm" | "cold";
};

export type ConversionLeads = {
  window_days: number;
  leads: ConversionLead[];
};

export type AuditLogEntry = {
  id: number;
  action: string;
  entity_type: string;
  entity_id: number | null;
  summary: string;
  employee_name: string | null;
  created_at: string;
};

export type CompanySummary = {
  id: number;
  name: string;
  phone: string | null;
  is_vip: boolean;
  needs_follow_up: boolean;
  high_risk: boolean;
};

export type ProfileTruck = {
  truck_number: string | null;
  license_plate: string | null;
  trailer_number: string | null;
  visits: number;
  last_seen: string | null;
};

export type ProfilePass = {
  id: number;
  pass_type: string;
  status: string;
  price: number;
  issue_date: string;
  expiration_date: string;
};

export type ProfilePayment = {
  amount: number;
  method: string;
  paid_at: string;
  receipt_number: string | null;
};

export type CompanyProfile = {
  id: number;
  name: string;
  phone: string | null;
  is_monthly: boolean;
  monthly_price: number | null;
  renewal_date: string | null;
  outstanding_balance: number;
  total_visits: number;
  total_spent: number;
  active_passes: number;
  first_seen: string | null;
  last_seen: string | null;
  loyalty_score: number;
  trucks: ProfileTruck[];
  recent_passes: ProfilePass[];
  recent_payments: ProfilePayment[];
};

export type LotCheckResult = {
  found: boolean;
  status?: "active" | "expiring_soon" | "expired" | "cancelled";
  company_name?: string;
  phone?: string;
  truck_number?: string;
  trailer_number?: string;
  license_plate?: string;
  pass_type?: "daily" | "weekly" | "monthly";
  expiration_date?: string;
  notes?: string;
  amount_paid?: number | null;
  payment_method?: "cash" | "check" | "credit_card" | "debit_card" | "phone_payment" | null;
  paid_at?: string | null;
  is_monthly_customer?: boolean;
  spot_number?: number | null;
  spot_label?: string | null;
};

export type VehicleType = "truck" | "trailer" | "bobtail" | "flatbed" | "car" | "other";
export type PassType = "daily" | "weekly" | "monthly";
export type PaymentMethod = "cash" | "credit_card" | "debit_card" | "check" | "phone";

export type IssuePassRequest = {
  company_name: string;
  truck_number?: string;
  trailer_number?: string;
  license_plate?: string;
  phone: string;
  vehicle_type: VehicleType;
  pass_type: PassType;
  price?: number;
  issue_date: string;
  end_date?: string;
  payment_method: PaymentMethod;
  check_number?: string;
};

export type CreatePaymentRequest = {
  kind: "issue" | "renew";
  issue?: {
    company_name: string;
    truck_number?: string;
    trailer_number?: string;
    license_plate?: string;
    phone: string;
    vehicle_type: VehicleType;
    pass_type: PassType;
    issue_date: string;
    end_date?: string;
    price?: number;
  };
  renew?: { pass_id: number; end_date: string };
};

export type PaymentRequestCreated = {
  token: string;
  pay_url: string;
  amount: number;
  summary: string;
  status: string;
};

export type PaymentRequestStatus = {
  status: "pending" | "paid" | "cancelled";
  kind: string;
  amount: number;
  summary: string;
  receipt_number: string | null;
};

export type CallItem = {
  priority: "now" | "today" | "worth_a_call";
  kind: "renewal_overdue" | "renewal_due" | "pass_expiring" | "overstay" | "lead";
  company_id: number | null;
  company_name: string;
  phone: string | null;
  reason: string;
  amount: number | null;
  monthly_customer_id: number | null;
  pass_id: number | null;
};

export type MorningReport = {
  generated_for: string;
  yesterday_revenue: number;
  todays_revenue: number;
  month_to_date_revenue: number;
  occupied_spaces: number;
  available_spaces: number;
  capacity: number;
  calls: CallItem[];
  all_clear: boolean;
};


export type ReminderCustomer = {
  monthly_customer_id: number;
  company_name: string;
  phone: string | null;
  monthly_price: number;
  renewal_date: string;
  days_until_renewal: number;
  reminder_status: string;
  last_reminder_at: string | null;
};

export type RemindersOverview = {
  sms_configured: boolean;
  auto_enabled: boolean;
  customers: ReminderCustomer[];
};

export type SendReminderResult = {
  sent: boolean;
  message: string;
  reminder_status: string;
};

export type SweepResult = {
  enabled: boolean;
  checked: number;
  sent: number;
  skipped: number;
};

export type PassVerifyResult = {
  valid: boolean;
  status: "active" | "expiring_soon" | "expired" | "cancelled" | null;
  company_name: string | null;
  truck_number: string | null;
  trailer_number: string | null;
  license_plate: string | null;
  pass_type: PassType | null;
  issue_date: string | null;
  expiration_date: string | null;
  price: number | null;
  receipt_number: string | null;
  spot_number: number | null;
  spot_label: string | null;
};

export type ReassignResult = {
  spot_number: number;
};

/** One cell of the lot grid — state is derived server-side from live passes. */
export type SpotState = {
  number: number;
  label: string;
  state: "free" | "occupied" | "expiring" | "grace" | "overstay" | "inactive";
  company_name: string | null;
  truck_number: string | null;
  pass_id: number | null;
  expiration_date: string | null;
};

export type MoveSpotRequest = { pass_id: number; to_number: number };
export type MoveSpotResult = { pass_id: number; spot_number: number; spot_label: string };

export type RenewPassRequest = {
  end_date: string;
  payment_method: PaymentMethod;
  check_number?: string;
  /** "continue" keeps the plan going (whole periods); "close_out" settles a
   *  departing customer for the time used and closes the account. */
  mode?: "continue" | "close_out";
};

export type CreateIntentRequest = {
  client_request_id: string;
  company_name: string;
  truck_number?: string;
  trailer_number?: string;
  license_plate?: string;
  phone: string;
  vehicle_type: VehicleType;
  pass_type: PassType;
  issue_date: string;
  end_date?: string;
};

export type CreateIntentResponse = {
  client_secret: string;
  payment_intent_id: string;
  amount: number;
};

export type FinalizeStripePaymentRequest = {
  payment_intent_id: string;
};

export type SearchResultItem = {
  type: "company" | "vehicle";
  label: string;
  sublabel?: string;
  query: string;
};

export type CompanyLookupResult = {
  found: boolean;
  company_id: number | null;
  monthly_price: number | null;
  trucks: { truck_number: string | null; license_plate: string | null; price: number; expiration_date: string }[];
};

export type PassRead = {
  id: number;
  pass_type: PassType;
  status: string;
  price: number;
  issue_date: string;
  expiration_date: string;
  receipt_number: string | null;
  qr_code: string | null;
  barcode: string | null;
  spot_number: number | null;
  spot_label: string | null;
};

export type PassListItem = {
  id: number;
  pass_type: PassType;
  status: "active" | "expiring_soon" | "expired" | "cancelled";
  price: number;
  issue_date: string;
  expiration_date: string;
  receipt_number: string | null;
  qr_code: string | null;
  spot_number: number | null;
  spot_label: string | null;
  company_name: string | null;
  company_id: number | null;
  truck_number: string | null;
  trailer_number: string | null;
  license_plate: string | null;
};

export type ReportsSummary = {
  revenue_series: { date: string; amount: number }[];
  revenue_30d: number;
  passes_30d: number;
  avg_price: number;
  active_companies: number;
  top_companies: { company_name: string; company_id: number | null; visits: number; total_paid: number }[];
  payment_methods: { method: string; count: number; total: number }[];
  frequent_trucks: { truck_number: string | null; company_name: string | null; visits: number }[];
  outstanding_balances: { company_name: string; balance: number }[];
};
