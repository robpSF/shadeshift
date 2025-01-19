import streamlit as st
import pandas as pd
import altair as alt

def main():
    st.title("ShadeShift (Disposition checker)")
    st.write(
        "Upload an Excel file with columns: "
        "**Name**, **Handle**, **Faction**, **Disposition**, **Tags**, **Bio**, "
        "**Image**, **TwFollowers**, **Permissions**, **WebsiteViews**"
    )

    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

    if uploaded_file is not None:
        # ---------------------
        # 1. Read Excel into DataFrame
        # ---------------------
        df = pd.read_excel(uploaded_file)

        # ---------------------
        # 2. Check for required columns
        # ---------------------
        required_columns = [
            "Name", "Faction", "Tags", 
            "Disposition", "TwFollowers", "WebsiteViews"
        ]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            st.error(f"Missing required columns: {missing_cols}")
            return

        # ---------------------
        # 3. Convert numeric columns where needed
        # ---------------------
        df["Disposition"] = pd.to_numeric(df["Disposition"], errors="coerce")
        df["TwFollowers"] = pd.to_numeric(df["TwFollowers"], errors="coerce")
        df["WebsiteViews"] = pd.to_numeric(df["WebsiteViews"], errors="coerce")

        # Drop rows with missing data in critical columns
        df.dropna(subset=["Disposition", "TwFollowers", "WebsiteViews"], inplace=True)

        # ---------------------
        # 4. Compute Reach = TwFollowers + WebsiteViews
        # ---------------------
        df["Reach"] = df["TwFollowers"] + df["WebsiteViews"]

        # Remove rows where Reach <= 0 (log scale needs positive)
        df = df[df["Reach"] > 0]

        # ---------------------
        # 5. Parse the CSV Tags into a list of tags
        # ---------------------
        # Create a new column of Python lists, e.g. ["tag1","tag2"] for a row
        df["TagList"] = df["Tags"].fillna("").apply(
            lambda x: [t.strip() for t in x.split(",") if t.strip() != ""]
        )

        # Gather all unique tags from the entire DataFrame
        all_unique_tags = sorted(set(tag for tags in df["TagList"] for tag in tags))

        # ---------------------
        # 6. Preview Data
        # ---------------------
        st.write("### Data Preview")
        st.dataframe(df.head())

        # ---------------------
        # 7. Filter by Faction
        # ---------------------
        all_factions = sorted(df["Faction"].dropna().unique())
        selected_factions = st.multiselect(
            label="Filter by Faction",
            options=all_factions,
            default=all_factions
        )
        df = df[df["Faction"].isin(selected_factions)]

        # ---------------------
        # 8. Filter by individual Tags
        # ---------------------
        selected_tags = st.multiselect(
            label="Filter by Tag",
            options=all_unique_tags,
            default=all_unique_tags
        )

        # If user de-selects everything, optionally show everything or nothing:
        # For now, we'll show only rows that match any selected tag (if tags are chosen)
        if selected_tags:
            df = df[df["TagList"].apply(lambda row_tags: any(t in row_tags for t in selected_tags))]

        st.write("### Disposition vs. Reach (Log Scale)")

        # ---------------------
        # 9. Toggle for using images vs. circle markers
        # ---------------------
        use_images = st.checkbox("Display images instead of circles", value=False)

        # If no rows left, warn and exit
        if df.empty:
            st.warning("No data available after filtering.")
            return

        # ---------------------
        # 10. Build the Altair chart
        # ---------------------

        # X-axis: Disposition
        x_axis = alt.X(
            "Disposition:Q",
            title="Disposition (Left: -5, Right: +5)",
            scale=alt.Scale(domain=(-5, 5))
        )

        # Y-axis: Reach (log scale)
        y_axis = alt.Y(
            "Reach:Q",
            title="Reach = TwFollowers + WebsiteViews (log scale)",
            scale=alt.Scale(type="log")
        )

        # Tooltip
        tooltip = ["Name", "Faction", "Tags", "Disposition", "Reach", "TwFollowers", "WebsiteViews"]

        if use_images:
            # Use the image URL from the 'Image' column
            chart = (
                alt.Chart(df)
                .mark_image(width=40, height=40)
                .encode(
                    x=x_axis,
                    y=y_axis,
                    url="Image:N",  # Should be a valid, accessible image URL
                    tooltip=tooltip
                )
                .interactive()
            )
        else:
            # Circle markers with color condition
            color_condition = alt.condition(
                "datum.Disposition < 0",
                alt.value("red"),
                alt.value("blue")
            )

            chart = (
                alt.Chart(df)
                .mark_circle(size=60)
                .encode(
                    x=x_axis,
                    y=y_axis,
                    color=color_condition,
                    tooltip=tooltip
                )
                .interactive()
            )

        st.altair_chart(chart, use_container_width=True)


if __name__ == "__main__":
    main()
