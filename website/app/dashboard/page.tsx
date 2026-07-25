import { redirect } from "next/navigation";
import { serverClient, adminClient } from "@/lib/supabase";
import { mintKey, getSpend } from "@/lib/litellm";
import Dashboard from "./Dashboard";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const supabase = serverClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  const admin = adminClient();
  let { data: profile } = await admin
    .from("profiles")
    .select("tier, litellm_key, persona, preferences")
    .eq("id", user.id)
    .maybeSingle();

  // ensure the row + key exist
  if (!profile) {
    await admin.from("profiles").insert({ id: user.id });
    profile = { tier: "free", litellm_key: null, persona: "", preferences: "" } as any;
  }
  let key = profile!.litellm_key as string | null;
  if (!key) {
    try {
      key = await mintKey(user.id, profile!.tier || "free");
      await admin.from("profiles").update({ litellm_key: key }).eq("id", user.id);
    } catch {
      key = null; // LiteLLM offline in dev — dashboard still renders
    }
  }

  const spend = key ? await getSpend(key) : { spend: 0, maxBudget: 0 };
  const { data: docs } = await admin
    .from("documents")
    .select("id, filename, status, created_at")
    .eq("user_id", user.id)
    .order("created_at", { ascending: false });

  return (
    <Dashboard
      email={user.email ?? ""}
      tier={profile!.tier || "free"}
      parakeetKey={key}
      spend={spend.spend}
      maxBudget={spend.maxBudget}
      persona={profile!.persona || ""}
      preferences={profile!.preferences || ""}
      docs={docs ?? []}
      siteUrl={process.env.NEXT_PUBLIC_SITE_URL || ""}
      ragUrl={
        process.env.SUPABASE_FUNCTIONS_URL
          ? `${process.env.SUPABASE_FUNCTIONS_URL.replace(/\/$/, "")}/rag`
          : `${process.env.NEXT_PUBLIC_SUPABASE_URL}/functions/v1/rag`
      }
    />
  );
}
