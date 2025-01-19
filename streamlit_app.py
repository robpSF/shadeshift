import streamlit as st
import pandas as pd
import altair as alt

def main():
    st.title("Excel Uploader & Disposition vs TwFollowers Chart")
    st.write(
        "Upload an Excel file with columns: "
        "**Name**, **Handle**, **Faction**, **Disposition**, **Tags**, "
        "**Bio**, **Image**, **TwFollowers**, **Permissions**, **WebsiteViews**"
    )

    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

    if uploaded_file is not None:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(uploaded_file)

        # Ensure required columns exist
        required_columns = ["Name", "Faction", "Tags", "Disposition", "TwFollowers"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            st.error(f"Missing required columns: {missing_cols}")
            return

        # Convert to numeric
        df["Disposition"] = pd.to_numeric(df["Disposition"], errors="coerce")
        df["TwFollowers"] = pd.to_numeric(df["TwFollowers"], errors="coerce")

        # Drop rows with invalid or missing values
        df = df.dropna(subset=["Disposition", "TwFollowers"])
        # A log scale requires strictly positive values; remove any 0 or negative TwFollowers
        df = df[df["TwFollowers"] > 0]

        st.write("### Data Preview")
        st.dataframe(df.head())

        # -------------------
        # Faction Filter
        # -------------------
        all_factions = sorted(df["Faction"].dropna().unique())
        selected_factions = st.multiselect(
            label="Filter by Faction",
            options=all_factions,
            default=all_factions
        )
        df = df[df["Faction"].isin(selected_factions)]

        # -------------------
        # Tag Filter
        # -------------------
        all_tags = sorted(df["Tags"].dropna().unique())
        selected_tags = st.multiselect(
            label="Filter by Tag",
            options=all_tags,
            default=all_tags
        )
        df = df[df["Tags"].isin(selected_tags)]

        st.write("### Disposition vs TwFollowers (Log Scale)")

        # Color points red if Disposition < 0, blue otherwise
        color_condition = alt.condition(
            "datum.Disposition < 0",  # A JavaScript expression
            alt.value("red"),         # Color if condition is true
            alt.value("blue")         # Color if condition is false
        )

        # Create the Altair chart
        chart = (
            alt.Chart(df)
            .mark_circle(size=60)
            .encode(
                x=alt.X(
                    "Disposition:Q",
                    title="Disposition (Left: -5, Right: +5)",
                    scale=alt.Scale(domain=(-5, 5))
                ),
                y=alt.Y(
                    "TwFollowers:Q",
                    title="Twitter Followers (log scale)",
                    scale=alt.Scale(type="log")
                ),
                color=color_condition,
                tooltip=["Name", "Faction", "Tags", "Disposition", "TwFollowers"]
            )
            .interactive()
        )

        st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    main()
