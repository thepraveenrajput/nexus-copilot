"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const router = useRouter();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleRegister = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setError("");

    if (!fullName.trim() || !email.trim() || !password || !confirmPassword) {
      setError("Please fill in all fields.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email.trim(),
          full_name: fullName.trim(),
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        let errorMessage = "Unable to create account.";

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
          : "Unable to create account. Please try again.",
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

          <h1 className="mt-6 text-[26px] font-semibold tracking-[-0.03em]">
            Create your account
          </h1>

          <p className="mt-2 text-[14px] text-[#667085]">
            Join your NexusCopilot enterprise workspace.
          </p>
        </div>

        {/* REGISTER CARD */}
        <form
          onSubmit={handleRegister}
          className="rounded-2xl border border-[#e4e7ec] bg-white p-7 shadow-[0_10px_35px_rgba(16,24,40,0.07)]"
        >
          {/* FULL NAME */}
          <div>
            <label
              htmlFor="fullName"
              className="text-[13px] font-medium text-[#344054]"
            >
              Full name
            </label>

            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              required
              autoComplete="name"
              placeholder="Your full name"
              className="mt-2 h-11 w-full rounded-xl border border-[#d0d5dd] bg-white px-3.5 text-[14px] text-[#101828] outline-none transition placeholder:text-[#98a2b3] hover:border-[#98a2b3] focus:border-[#111318] focus:ring-2 focus:ring-black/5"
            />
          </div>

          {/* EMAIL */}
          <div className="mt-5">
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
            <label
              htmlFor="password"
              className="text-[13px] font-medium text-[#344054]"
            >
              Password
            </label>

            <div className="relative mt-2">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                autoComplete="new-password"
                placeholder="At least 8 characters"
                className="h-11 w-full rounded-xl border border-[#d0d5dd] bg-white px-3.5 pr-20 text-[14px] text-[#101828] outline-none transition placeholder:text-[#98a2b3] hover:border-[#98a2b3] focus:border-[#111318] focus:ring-2 focus:ring-black/5"
              />

              <button
                type="button"
                onClick={() => setShowPassword((current) => !current)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[12px] font-medium text-[#667085] hover:text-[#111318]"
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          {/* CONFIRM PASSWORD */}
          <div className="mt-5">
            <label
              htmlFor="confirmPassword"
              className="text-[13px] font-medium text-[#344054]"
            >
              Confirm password
            </label>

            <div className="relative mt-2">
              <input
                id="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                required
                autoComplete="new-password"
                placeholder="Re-enter your password"
                className="h-11 w-full rounded-xl border border-[#d0d5dd] bg-white px-3.5 pr-20 text-[14px] text-[#101828] outline-none transition placeholder:text-[#98a2b3] hover:border-[#98a2b3] focus:border-[#111318] focus:ring-2 focus:ring-black/5"
              />

              <button
                type="button"
                onClick={() => setShowConfirmPassword((current) => !current)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[12px] font-medium text-[#667085] hover:text-[#111318]"
              >
                {showConfirmPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          {/* ERROR */}
          {error && (
            <div className="mt-4 rounded-xl border border-[#fecdca] bg-[#fef3f2] px-3.5 py-3 text-[12px] leading-5 text-[#b42318]">
              {error}
            </div>
          )}

          {/* REGISTER */}
          <button
            type="submit"
            disabled={loading}
            className="mt-6 h-11 w-full rounded-xl bg-black text-[14px] font-medium text-white transition hover:bg-[#1d1d1f] active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Creating account...
              </span>
            ) : (
              "Create account"
            )}
          </button>
        </form>

        {/* LOGIN LINK */}
        <div className="mt-6 text-center">
          <p className="text-[13px] text-[#667085]">
            Already have an account?{" "}
            <button
              type="button"
              onClick={() => router.push("/login")}
              className="font-medium text-[#111318] hover:underline"
            >
              Sign in
            </button>
          </p>

          <p className="mt-4 text-[11px] text-[#98a2b3]">
            NexusCopilot
            <span className="mx-1.5">·</span>
            Enterprise AI Knowledge Platform
          </p>
        </div>

        {/* SECURITY */}
        <div className="mt-5 flex items-center justify-center gap-2 text-[10px] text-[#98a2b3]">
          <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
          Secure enterprise authentication
        </div>
      </div>
    </main>
  );
}
