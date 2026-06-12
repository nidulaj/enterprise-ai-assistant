import {createClient} from "@supabase/supabase-js";

const superbaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL as string;
const superbaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY as string;

export const superbase = createClient(
    superbaseUrl,
    superbaseAnonKey
)