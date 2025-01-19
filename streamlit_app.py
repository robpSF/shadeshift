import streamlit as st
import pandas as pd
import altair as alt

def main():
    st.title("Excel Uploader: Disposition vs. Reach (TwFollowers + WebsiteViews)")
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
        # 3. Convert to numeric
        # ---------------------
        df["Disposition"] = pd.to_numeric(df["Disposition"], errors="coerce")
        df["TwFollowers"] = pd.to_numeric(df["TwFollowers"], errors="coerce")
        df["WebsiteViews"] = pd.to_numeric(df["WebsiteViews"], errors="coerce")

        # Drop rows that have NaN in critical columns
        df.dropna(subset=["Disposition", "TwFollowers", "WebsiteViews"], inplace=True)

        # ---------------------
        # 4. Compute Reach = TwFollowers + WebsiteViews
        # ---------------------
        df["Reach"] = df["TwFollowers"] + df["WebsiteViews"]
        
        # Remove rows where Reach <= 0 (log scale requires > 0)
        df = df[df["Reach"] > 0]

        # ---------------------
        # 5. Preview Data
        # ---------------------
        st.write("### Data Preview")
        st.dataframe(df.head())

        # ---------------------
        # 6. Filters (Faction & Tags)
        # ---------------------
        all_factions = sorted(df["Faction"].dropna().unique())
        selected_factions = st.multiselect(
            label="Filter by Faction",
            options=all_factions,
            default=all_factions
        )
        df = df[df["Faction"].isin(selected_factions)]

        all_tags = sorted(df["Tags"].dropna().unique())
        selected_tags = st.multiselect(
            label="Filter by Tag",
            options=all_tags,
            default=all_tags
        )
        df = df[df["Tags"].isin(selected_tags)]

        st.write("### Disposition vs. Reach (Log Scale)")

        # ---------------------
        # 7. Toggle for using images vs. circle markers
        # ---------------------
        use_images = st.checkbox("Display images instead of circles", value=False)

        # ---------------------
        # 8. Build the Altair chart
        # ---------------------
        if df.empty:
            st.warning("No data available after filtering.")
            return

        # X-axis: Disposition (fixed domain from -5 to 5)
        x_axis = alt.X(
            "Disposition:Q",
            title="Disposition (Left: -5, Right: +5)",
            scale=alt.Scale(domain=(-6, 6))
        )

        # Y-axis: Reach (log scale)
        y_axis = alt.Y(
            "Reach:Q",
            title="Reach = TwFollowers + WebsiteViews (log scale)",
            scale=alt.Scale(type="log")
        )

        # Common tooltip
        tooltip = ["Name", "Faction", "Tags", "Disposition", "Reach", "TwFollowers", "WebsiteViews"]

        if use_images:
            # If using images, mark_image must have 'url' bound to the "Image" column
            # Note: mark_image doesn't support color channel for the images themselves
            chart = (
                alt.Chart(df)
                .mark_image(width=40, height=40)
                .encode(
                    x=x_axis,
                    y=y_axis,
                    url="Image:N",  # The image URL should be in this column
                    tooltip=tooltip
                )
                .interactive()
            )
        else:
            # Circle markers with color condition
            color_condition = alt.condition(
                "datum.Disposition < 0",  # A JavaScript expression
                alt.value("red"),         # Color if true
                alt.value("blue")         # Color if false
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
