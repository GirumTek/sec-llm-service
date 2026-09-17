import { useState } from "react";
import { SelectField, TextField, Button, View } from "@aws-amplify/ui-react";
import "./ChatForm.css";

const COMPANIES: Record<string, string> = {
  Apple: "AAPL",
  Amazon: "AMZN",
  Microsoft: "MSFT",
  Google: "GOOGL",
  NVIDIA: "NVDA",
  Meta: "META",
};

const PERIODS = ["Q1", "Q2", "Q3", "Q4", "FY"];

interface RequestBody {
  question: string;
  ticker: string;
  year: number;
  period: string;
}

interface ResponseBody {
  answer: string;
  meta: object;
}

async function submitQuery(body: RequestBody): Promise<ResponseBody> {
  console.log("Request:", JSON.stringify(body, null, 2));
  await new Promise((r) => setTimeout(r, 800));
  return { answer: "Stub response — replace with real Lambda call.", meta: {} };
}

export default function ChatForm() {
  const [company, setCompany] = useState<string>("");
  const [year, setYear] = useState<number>(new Date().getFullYear());
  const [period, setPeriod] = useState<string>("");
  const [question, setQuestion] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState<string | null>(null);

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

  async function handleSubmit() {
    const body: RequestBody = {
      question,
      ticker: COMPANIES[company],
      year: Number(year),
      period,
    };

    setLoading(true);
    setError(null);

    try {
      const result = await submitQuery(body);
      setAnswer(result.answer);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong.");
      }
    } finally {
      setLoading(false);
    }
  }

   return (
    <div className="doc">
      <header className="doc-header">
        <h1>Partner Bot</h1>
        <p className="doc-subtitle">Ask a question about a company's SEC filing.</p>
      </header>

      <div className="doc-form">
        <SelectField
          label="Company"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
        >
          <option value="">Select a company</option>
          {Object.keys(COMPANIES).map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </SelectField>

        <div className="doc-row">
          <SelectField
            label="Year"
            value={String(year)}
            onChange={(e) => setYear(Number(e.target.value))}
          >
            {years.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </SelectField>

          <SelectField
            label="Period"
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
          >
            <option value="">Select a period</option>
            {PERIODS.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </SelectField>
        </div>

        <TextField
          label="Question"
          placeholder="What changed in operating expenses this quarter?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />

        <Button
          onClick={handleSubmit}
          isLoading={loading}
          loadingText="Reading filing…"
          className="doc-submit"
        >
          Ask
        </Button>
      </div>

      {error && <div className="doc-error">{error}</div>}

      {answer && (
        <div className="doc-answer">
          <div className="doc-answer-label">
            {COMPANIES[company] || company} · {period} {year}
          </div>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}