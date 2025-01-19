import streamlit as st
import pandas as pd
import altair as alt

def main():
    st.title("Excel Uploader & Disposition vs TwFollowers Chart")
    st.write("Upload an Excel file with columns: Name, Handle, Faction, Disposition, Tags, Bio, Image, TwFollowers, Permissions, WebsiteViews")

    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

    if uploaded_file is not None:
        # Read the Excel file
        df = pd.read_excel(uploaded_file)

        # Make sure the needed columns exist
        required_columns = ["Name", "Disposition", "TwFollowers"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            st.error(f"Missing required columns: {missing_cols}")
            return

        # Convert to numeric
        df["Disposition"] = pd.to_numeric(df["Disposition"], errors="coerce")
        df["TwFollowers"] = pd.to_numeric(df["TwFollowers"], errors="coerce")

        # Drop rows with invalid data or zero/negative TwFollowers
        df = df.dropna(subset=["Disposition", "TwFollowers"])
        df = df[df["TwFollowers"] > 0]

        st.write("### Data Preview")
        st.dataframe(df.head())

        st.write("### Disposition vs TwFollowers (Log Scale)")

        # Create Altair chart with auto y-domain
        chart = (
            alt.Chart(df)
            .mark_circle(size=60)
            .encode(
                x=alt.X(
                    "Disposition:Q",
                    title="Disposition (Left: -5, Right: +5)",
                    # Remove domain if you want to let data drive x-axis
                    scale=alt.Scale(domain=(-5, 5))
                ),
                y=alt.Y(
                    "TwFollowers:Q",
                    title="Twitter Followers (log scale)",
                    scale=alt.Scale(type="log")
                    # No domain => automatically determined by Altair
                ),
                tooltip=["Name", "Disposition", "TwFollowers"]
            )
            .interactive()
        )

        st.altair_chart(chart, use_container_width=True)

if __name__ == "__main__":
    main()
