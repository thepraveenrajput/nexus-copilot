"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!email.trim() || !password.trim()) {
      setError("Please enter your email and password.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email.trim(),
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        let errorMessage = "Invalid email or password.";

        if (typeof data.detail === "string") {
          errorMessage = data.detail;
        } else if (Array.isArray(data.detail)) {
          errorMessage = data.detail
            .map((error: { msg?: string }) => error.msg || "Invalid input.")
            .join(", ");
        }

        throw new Error(errorMessage);
      }

      localStorage.setItem("nexus_access_token", data.access_token);

      localStorage.setItem("nexus_user", JSON.stringify(data.user));

      router.push("/");
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Unable to sign in. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#f5f6f8] px-5 py-10 text-[#111318]">
      <div className="w-full max-w-[420px]">
        {/* BRAND */}
        <div className="mb-8 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-black text-xl font-bold text-white shadow-[0_8px_25px_rgba(0,0,0,0.12)]">
            N
          </div>

          <h1 className="mt-6 text-[26px] font-semibold tracking-[-0.03em] text-[#111318]">
            Welcome to NexusCopilot
          </h1>

          <p className="mt-2 text-[14px] text-[#667085]">
            Sign in to your enterprise AI workspace.
          </p>
        </div>

        {/* LOGIN CARD */}
        <form
          onSubmit={handleLogin}
          className="rounded-2xl border border-[#e4e7ec] bg-white p-7 shadow-[0_10px_35px_rgba(16,24,40,0.07)]"
        >
          {/* EMAIL */}
          <div>
            <label
              htmlFor="email"
              className="text-[13px] font-medium text-[#344054]"
            >
              Email address
            </label>

            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              autoComplete="email"
              placeholder="you@company.com"
              className="mt-2 h-11 w-full rounded-xl border border-[#d0d5dd] bg-white px-3.5 text-[14px] text-[#101828] outline-none transition placeholder:text-[#98a2b3] hover:border-[#98a2b3] focus:border-[#111318] focus:ring-2 focus:ring-black/5"
            />
          </div>

          {/* PASSWORD */}
          <div className="mt-5">
            <div className="flex items-center justify-between">
              <label
                htmlFor="password"
                className="text-[13px] font-medium text-[#344054]"
              >
                Password
              </label>
            </div>

            <div className="relative mt-2">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                autoComplete="current-password"
                placeholder="Enter your password"
                className="h-11 w-full rounded-xl border border-[#d0d5dd] bg-white px-3.5 pr-20 text-[14px] text-[#101828] outline-none transition placeholder:text-[#98a2b3] hover:border-[#98a2b3] focus:border-[#111318] focus:ring-2 focus:ring-black/5"
              />

              <button
                type="button"
                onClick={() => setShowPassword((current) => !current)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[12px] font-medium text-[#667085] transition hover:text-[#111318]"
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          {/* ERROR */}
          {error && (
            <div className="mt-4 rounded-xl border border-[#fecdca] bg-[#fef3f2] px-3.5 py-3 text-[12px] leading-5 text-[#b42318]">
              {error}
            </div>
          )}

          {/* SIGN IN */}
          <button
            type="submit"
            disabled={loading}
            className="mt-6 h-11 w-full rounded-xl bg-black text-[14px] font-medium text-white transition hover:bg-[#1d1d1f] active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Signing in...
              </span>
            ) : (
              "Sign in"
            )}
          </button>
        </form>

        {/* REGISTER LINK */}
        <div className="mt-6 text-center">
          <p className="text-[13px] text-[#667085]">
            Don&apos;t have an account?{" "}
            <button
              type="button"
              onClick={() => router.push("/register")}
              className="font-medium text-[#111318] hover:underline"
            >
              Create account
            </button>
          </p>

          <p className="mt-4 text-[11px] text-[#98a2b3]">
            NexusCopilot
            <span className="mx-1.5">·</span>
            Enterprise AI Knowledge Platform
          </p>
        </div>

        {/* SECURITY TEXT */}
        <div className="mt-5 flex items-center justify-center gap-2 text-[10px] text-[#98a2b3]">
          <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
          Secure enterprise authentication
        </div>
      </div>
    </main>
  );
}
