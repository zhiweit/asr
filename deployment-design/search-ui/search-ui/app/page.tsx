"use client";

import React from "react";
import {
  SearchProvider,
  SearchBox,
  Results,
  Facet,
  PagingInfo,
  ResultsPerPage,
  Paging,
} from "@elastic/react-search-ui";
import { Layout } from "@elastic/react-search-ui-views";
import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";

// import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import "@elastic/react-search-ui-views/lib/styles/styles.css";
import { SearchDriverOptions } from "@elastic/search-ui";

if (!process.env.NEXT_PUBLIC_ELASTICSEARCH_HOST) {
  throw new Error("NEXT_PUBLIC_ELASTICSEARCH_HOST is not set");
}
if (!process.env.NEXT_PUBLIC_ELASTICSEARCH_API_KEY) {
  throw new Error("NEXT_PUBLIC_ELASTICSEARCH_API_KEY is not set");
}
if (!process.env.NEXT_PUBLIC_ELASTICSEARCH_INDEX) {
  throw new Error("NEXT_PUBLIC_ELASTICSEARCH_INDEX is not set");
}

const connector = new ElasticsearchAPIConnector({
  host: process.env.NEXT_PUBLIC_ELASTICSEARCH_HOST,
  apiKey: process.env.NEXT_PUBLIC_ELASTICSEARCH_API_KEY,
  index: process.env.NEXT_PUBLIC_ELASTICSEARCH_INDEX,
});

const config: SearchDriverOptions = {
  apiConnector: connector,
  searchQuery: {
    search_fields: {
      generated_text: {},
      age: {},
      gender: {},
      accent: {},
    },
    result_fields: {
      text: {
        snippet: { size: 200, fallback: true },
        raw: {},
      },
      up_votes: { raw: {} },
      down_votes: { raw: {} },
      generated_text: { snippet: { size: 200, fallback: true } },
      duration: { raw: {} },
      age: { raw: {} },
      gender: { raw: {} },
      accent: { raw: {} },
    },
  },
  alwaysSearchOnInitialLoad: true,
};

export default function Home() {
  return (
    <SearchProvider config={config}>
      <Layout
        header={<SearchBox />}
        sideContent={
          <div className="p-4">
            <h3 className="text-lg font-semibold mb-3">Filters</h3>
            <div className="mb-4">
              <Facet field="duration" label="Duration" />
            </div>
            <div className="mb-4">
              <Facet field="age" label="Age" />
            </div>
            <div className="mb-4">
              <Facet field="gender" label="Gender" />
            </div>
            <div className="mb-4">
              <Facet field="accent" label="Accent" />
            </div>
          </div>
        }
        bodyContent={
          <div>
            <PagingInfo />
            <ResultsPerPage />
            <Results
              titleField="generated_text"
              resultView={({ result }) => (
                <div className="result-item p-4 bg-gray-100 rounded-lg mb-4">
                  {/* Display original text */}
                  {result.text && (result.text.snippet || result.text.raw) && (
                    <div className="mb-3">
                      <h3 className="text-lg font-semibold mb-2">
                        Original Text:
                      </h3>
                      <div
                        className="p-3 bg-green-50 border border-green-200 rounded"
                        dangerouslySetInnerHTML={{
                          __html: result.text.snippet || result.text.raw,
                        }}
                      />
                    </div>
                  )}
                  {/* Display highlighted snippet with proper styling */}
                  {result.generated_text.snippet && (
                    <div className="mb-3">
                      <h3 className="text-lg font-semibold mb-2">
                        Matching Content (generated text):
                      </h3>
                      <div
                        className="p-3 bg-yellow-50 border border-yellow-200 rounded"
                        dangerouslySetInnerHTML={{
                          __html: result.generated_text.snippet,
                        }}
                      />
                    </div>
                  )}
                  <ul className="mt-2">
                    <li className="mb-1">
                      <strong>Duration:</strong> {result.duration.raw} seconds
                    </li>
                    <li className="mb-1">
                      <strong>Age:</strong> {result.age.raw}
                    </li>
                    <li className="mb-1">
                      <strong>Gender:</strong> {result.gender.raw}
                    </li>
                    <li className="mb-1">
                      <strong>Accent:</strong> {result.accent.raw}
                    </li>
                  </ul>
                </div>
              )}
            />
            <Paging />

            {/* <Sorting
              label={"Sort by"}
              sortOptions={[
                { name: "Relevance", value: "", direction: "" },
                { name: "Duration (asc)", value: "duration", direction: "asc" },
                {
                  name: "Duration (desc)",
                  value: "duration",
                  direction: "desc",
                },
              ]}
            /> */}
          </div>
        }
      />
    </SearchProvider>
  );
}
