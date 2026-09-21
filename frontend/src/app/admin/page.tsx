"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type AuditLog = {
  id: number;
  user_id: number | null;
  conversation_id: number | null;
  action: string;
  route: string | null;
  agent: string | null;
  question: string | null;
  success: boolean;
  duration_ms: number | null;
  created_at: string;
};

type Analytics = {
  total_queries: number;
  successful_queries: number;
  failed_queries: number;
  rag_queries: number;
  sql_queries: number;
  hybrid_queries: number;
  average_response_time_ms: number;
};

export default function AdminPage() {
  const router = useRouter();

  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("nexus_access_token");
    const userRaw = localStorage.getItem("nexus_user");

    if (!token || !userRaw) {
      router.replace("/login");
      return;
    }

    try {
      const user = JSON.parse(userRaw);

      if (user.role !== "admin" && user.role !== "administrator") {
        router.replace("/");
        return;
      }
    } catch {
      router.replace("/login");
      return;
    }

    const headers = {
      Authorization: `Bearer ${token}`,
    };

    Promise.all([
      fetch("http://127.0.0.1:8000/admin/audit-logs", {
        headers,
      }),

      fetch("http://127.0.0.1:8000/admin/analytics", {
        headers,
      }),
    ])
      .then(async ([logsResponse, analyticsResponse]) => {
        if (logsResponse.status === 401 || analyticsResponse.status === 401) {
          localStorage.removeItem("nexus_access_token");

          localStorage.removeItem("nexus_user");

          router.replace("/login");
          return;
        }

        if (logsResponse.status === 403 || analyticsResponse.status === 403) {
          router.replace("/");
          return;
        }

        if (!logsResponse.ok) {
          throw new Error("Failed to load audit logs.");
        }

        if (!analyticsResponse.ok) {
          throw new Error("Failed to load analytics.");
        }

        const logsData = await logsResponse.json();

        const analyticsData = await analyticsResponse.json();

        setLogs(logsData);
        setAnalytics(analyticsData);
      })
      .catch((err) => {
        console.error(err);
        setError("Unable to load admin analytics.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [router]);

  return (
    <main className="min-h-screen bg-[#f7f8fa] px-6 py-8 text-slate-900">
      <div className="mx-auto max-w-7xl">
        {/* Header */}

        <div className="mb-8 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-slate-500">NexusCopilot</p>

            <h1 className="mt-1 text-3xl font-semibold">Admin Dashboard</h1>

            <p className="mt-2 text-sm text-slate-500">
              Monitor AI activity, routing and event-driven analytics.
            </p>
          </div>

          <button
            onClick={() => router.push("/")}
            className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium hover:bg-slate-50"
          >
            Back to Copilot
          </button>
        </div>

        {/* Error */}

        {error && (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Main Stats */}

        <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-4">
          {/* Total Queries */}

          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <p className="text-sm text-slate-500">Total Queries</p>

            <p className="mt-2 text-3xl font-semibold">
              {analytics?.total_queries ?? 0}
            </p>
          </div>

          {/* Successful */}

          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <p className="text-sm text-slate-500">Successful</p>

            <p className="mt-2 text-3xl font-semibold">
              {analytics?.successful_queries ?? 0}
            </p>
          </div>

          {/* Failed */}

          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <p className="text-sm text-slate-500">Failed</p>

            <p className="mt-2 text-3xl font-semibold">
              {analytics?.failed_queries ?? 0}
            </p>
          </div>

          {/* Average Response */}

          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <p className="text-sm text-slate-500">Avg Response</p>

            <p className="mt-2 text-3xl font-semibold">
              {analytics?.average_response_time_ms ?? 0}

              <span className="ml-1 text-base font-normal text-slate-500">
                ms
              </span>
            </p>
          </div>
        </div>

        {/* Routing Analytics */}

        <div className="mb-8">
          <div className="mb-4">
            <h2 className="text-lg font-semibold">Query Routing</h2>

            <p className="mt-1 text-sm text-slate-500">
              Queries processed by each AI route.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {/* RAG */}

            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-slate-600">
                  RAG Queries
                </p>

                <span className="rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">
                  RAG
                </span>
              </div>

              <p className="mt-4 text-3xl font-semibold">
                {analytics?.rag_queries ?? 0}
              </p>
            </div>

            {/* SQL */}

            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-slate-600">
                  SQL Queries
                </p>

                <span className="rounded-md bg-purple-50 px-2 py-1 text-xs font-medium text-purple-700">
                  SQL
                </span>
              </div>

              <p className="mt-4 text-3xl font-semibold">
                {analytics?.sql_queries ?? 0}
              </p>
            </div>

            {/* Hybrid */}

            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-slate-600">
                  Hybrid Queries
                </p>

                <span className="rounded-md bg-orange-50 px-2 py-1 text-xs font-medium text-orange-700">
                  Hybrid
                </span>
              </div>

              <p className="mt-4 text-3xl font-semibold">
                {analytics?.hybrid_queries ?? 0}
              </p>
            </div>
          </div>
        </div>

        {/* Audit Logs */}

        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
          <div className="border-b border-slate-200 px-6 py-4">
            <h2 className="font-semibold">Recent AI Activity</h2>

            <p className="mt-1 text-sm text-slate-500">
              Latest audit events from NexusCopilot.
            </p>
          </div>

          {loading && (
            <div className="px-6 py-10 text-center text-sm text-slate-500">
              Loading analytics...
            </div>
          )}

          {!loading && !error && logs.length === 0 && (
            <div className="px-6 py-10 text-center text-sm text-slate-500">
              No audit events found.
            </div>
          )}

          {!loading && !error && logs.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="px-6 py-3">User</th>

                    <th className="px-6 py-3">Route</th>

                    <th className="px-6 py-3">Agent</th>

                    <th className="px-6 py-3">Question</th>

                    <th className="px-6 py-3">Status</th>

                    <th className="px-6 py-3">Duration</th>

                    <th className="px-6 py-3">Time</th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-100">
                  {logs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-50">
                      <td className="whitespace-nowrap px-6 py-4">
                        User #{log.user_id ?? "-"}
                      </td>

                      <td className="px-6 py-4">
                        <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-medium">
                          {log.route || "-"}
                        </span>
                      </td>

                      <td className="px-6 py-4">{log.agent || "-"}</td>

                      <td className="max-w-md px-6 py-4">
                        <p className="truncate">{log.question || "-"}</p>
                      </td>

                      <td className="px-6 py-4">
                        {log.success ? (
                          <span className="rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-green-700">
                            Success
                          </span>
                        ) : (
                          <span className="rounded-md bg-red-50 px-2 py-1 text-xs font-medium text-red-700">
                            Failed
                          </span>
                        )}
                      </td>

                      <td className="whitespace-nowrap px-6 py-4">
                        {log.duration_ms ?? "-"} ms
                      </td>

                      <td className="whitespace-nowrap px-6 py-4 text-slate-500">
                        {new Date(log.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
