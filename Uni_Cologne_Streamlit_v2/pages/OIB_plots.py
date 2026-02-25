import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

@st.cache_data
def load_data():
    df = pd.read_excel(
        r'UniCologne_Streamlit/Data/Hardardottir_Jackson_2025_Chem_Geol_adjusted.xlsx', 
        sheet_name='Tabelle1', 
        header=4
    )
    df[1] = 1
    plot_cols = df.columns[df.columns.str.contains('Plot', case=False, na=False)]
    if len(plot_cols) == 0:
        st.error("Keine Spalten mit 'Plot' im Namen gefunden.")
        st.stop()
    plots = df.loc[:, plot_cols].copy()
    plots.columns = plots.iloc[0].astype(str)
    plots = plots.iloc[1:].reset_index(drop=True)
    plots[1] = 1
    return plots

def main():
    st.title("OIB Plot Streamlit App")

    OIB_plots = load_data()

    method = st.selectbox("Method:", ['ID', 'ICP-MS'], index=1)
    if method == 'ID':
        mask = ~OIB_plots.columns.str.contains('ICP-MS', case=False, na=False)
    else:
        mask = ~OIB_plots.columns.str.contains('ID', case=False, na=False)
    sub_df = OIB_plots.loc[:, mask].copy()
    sub_df.columns = sub_df.iloc[0].astype(str)
    sub_df = sub_df.iloc[1:].reset_index(drop=True)
    bg_df = sub_df.copy()

    # Hotspot Auswahl
    hotspot_options = ['Nicht angegeben' if pd.isna(opt) else str(opt) for opt in sub_df['Hotspot'].unique()]
    hotspot_options = sorted(set(hotspot_options))
    all_hotspot = st.checkbox("All Hotspots", value=True)
    selected_hotspots = st.multiselect("Choose Hotspots:", hotspot_options, disabled=all_hotspot)

    # Island Auswahl
    def get_island_options(hotspots):
        if not hotspots:
            return ['All Islands']
        mask_hot = sub_df['Hotspot'].isna() if 'Nicht angegeben' in hotspots else False
        hot_vals = [h for h in hotspots if h != 'Nicht angegeben']
        if hot_vals:
            mask_hot = mask_hot | sub_df['Hotspot'].isin(hot_vals)
        available_islands = sub_df[mask_hot]['Island or seamount'].unique()
        clean_islands = ['Nicht angegeben' if pd.isna(i) else str(i) for i in available_islands]
        return ['All Islands'] + sorted(set(clean_islands))

    if all_hotspot or not selected_hotspots:
        island_options = ['All Islands']
    else:
        island_options = get_island_options(selected_hotspots)
    selected_islands = st.multiselect("Choose Islands:", island_options, default=['All Islands'])

    # Filter DataFrame
    filtered_df = sub_df.copy()
    if not all_hotspot and selected_hotspots:
        if 'Nicht angegeben' in selected_hotspots:
            nan_mask = filtered_df['Hotspot'].isna()
            val_mask = filtered_df['Hotspot'].isin([h for h in selected_hotspots if h != 'Nicht angegeben'])
            filtered_df = filtered_df[nan_mask | val_mask]
        else:
            filtered_df = filtered_df[filtered_df['Hotspot'].isin(selected_hotspots)]
    if 'All Islands' not in selected_islands:
        filtered_df = filtered_df[filtered_df['Island or seamount'].astype(str).isin(selected_islands)]

    st.write(f"Gefilterte Form: {filtered_df.shape}")
    if selected_hotspots:
        st.write(f"Aktive Hotspot-Filter: {', '.join(selected_hotspots)}")
    if 'All Islands' not in selected_islands:
        st.write(f"Aktiver Island-Filter: {', '.join(selected_islands)}")

    # Achsen-Auswahl
    available_columns = list(filtered_df.columns)
    col1_index = available_columns.index("1") if "1" in available_columns else 0
    x1 = st.selectbox("X1:", available_columns, index=col1_index)
    x2 = st.selectbox("X2:", available_columns, index=col1_index)
    y1 = st.selectbox("Y1:", available_columns, index=col1_index)
    y2 = st.selectbox("Y2:", available_columns, index=col1_index)
    # Add the log scale checkboxes
    col1, col2 = st.columns(2)
    with col1:
        x_log = st.checkbox("Log scale for X-axis", value=False)
    with col2:
        y_log = st.checkbox("Log scale for Y-axis", value=False)

    # Achsenlimits and autoscale button
    autoscale_btn = st.button("Autoscale axes")

    # Compute ratios
    def compute_full_ratios(df, x1, x2, y1, y2):
        x_num = pd.to_numeric(df[x1], errors='coerce')
        x_den = pd.to_numeric(df[x2], errors='coerce')
        y_num = pd.to_numeric(df[y1], errors='coerce')
        y_den = pd.to_numeric(df[y2], errors='coerce')
        with np.errstate(divide='ignore', invalid='ignore'):
            x_ratio_full = x_num / x_den
            y_ratio_full = y_num / y_den
        return x_ratio_full, y_ratio_full

    x_ratio_full, y_ratio_full = compute_full_ratios(filtered_df, x1, x2, y1, y2)
    valid_all = x_ratio_full.notna() & y_ratio_full.notna() & np.isfinite(x_ratio_full) & np.isfinite(y_ratio_full)
    x_vals_autoscale = x_ratio_full[valid_all]
    y_vals_autoscale = y_ratio_full[valid_all]

    # Background ratios
    if show_background := st.checkbox("Alle Hotspots im Hintergrund", value=False):
        x_bg, y_bg = compute_full_ratios(bg_df, x1, x2, y1, y2)
        valid_bg = x_bg.notna() & y_bg.notna() & np.isfinite(x_bg) & np.isfinite(y_bg)
        x_bg_vals = x_bg[valid_bg]
        y_bg_vals = y_bg[valid_bg]
        if x_log:
            x_bg_vals = x_bg_vals[x_bg_vals > 0]
        if y_log:
            y_bg_vals = y_bg_vals[y_bg_vals > 0]
        x_all_vals = pd.concat([
            x_vals_autoscale[x_vals_autoscale > 0] if x_log else x_vals_autoscale,
            x_bg_vals
        ])
        y_all_vals = pd.concat([
            y_vals_autoscale[y_vals_autoscale > 0] if y_log else y_vals_autoscale,
            y_bg_vals
        ])
    else:
        x_all_vals = x_vals_autoscale[x_vals_autoscale > 0] if x_log else x_vals_autoscale
        y_all_vals = y_vals_autoscale[y_vals_autoscale > 0] if y_log else y_vals_autoscale

    # Use session state to keep values persistent and editable
    if "x_min" not in st.session_state: st.session_state.x_min = 0.0
    if "x_max" not in st.session_state: st.session_state.x_max = 1.0
    if "y_min" not in st.session_state: st.session_state.y_min = 0.0
    if "y_max" not in st.session_state: st.session_state.y_max = 1.0

    # Autoscale logic
    if autoscale_btn:
        st.session_state.x_min = float(x_all_vals.min()) if not x_all_vals.empty else 0.0
        st.session_state.x_max = float(x_all_vals.max()) if not x_all_vals.empty else 1.0
        st.session_state.y_min = float(y_all_vals.min()) if not y_all_vals.empty else 0.0
        st.session_state.y_max = float(y_all_vals.max()) if not y_all_vals.empty else 1.0

    # Always show manual controls (use session_state for prefill)
    st.session_state.x_min = st.number_input("X min:", value=st.session_state.x_min, key="x_min_num")
    st.session_state.x_max = st.number_input("X max:", value=st.session_state.x_max, key="x_max_num")
    st.session_state.y_min = st.number_input("Y min:", value=st.session_state.y_min, key="y_min_num")
    st.session_state.y_max = st.number_input("Y max:", value=st.session_state.y_max, key="y_max_num")

    x_min = st.session_state.x_min
    x_max = st.session_state.x_max
    y_min = st.session_state.y_min
    y_max = st.session_state.y_max

    fig, ax = plt.subplots(figsize=(6,6), dpi=150)

    # Hintergrunddaten
    if show_background and bg_df is not None:
        ax.scatter(x_bg_vals, y_bg_vals, color='gray', alpha=0.5, label='Alle Daten', zorder=1, edgecolors='none', s=40)

    # Gruppierungslogik
    def labelize(arr):
        return ['Nicht angegeben' if pd.isna(v) else str(v) for v in arr]

    if all_hotspot:
        group_keys = sorted(labelize(filtered_df['Hotspot'].unique()), key=lambda x: (x == 'Nicht angegeben', x))
        def make_mask(g):
            return filtered_df['Hotspot'].isna() if g == 'Nicht angegeben' else (filtered_df['Hotspot'].astype(str) == g)
    elif len(selected_hotspots) > 1:
        group_keys = selected_hotspots
        def make_mask(g):
            return filtered_df['Hotspot'].isna() if g == 'Nicht angegeben' else (filtered_df['Hotspot'].astype(str) == g)
    elif len(selected_hotspots) == 1:
        hs = selected_hotspots[0]
        mask_hot = filtered_df['Hotspot'].isna() if hs == 'Nicht angegeben' else (filtered_df['Hotspot'].astype(str) == hs)
        islands = labelize(filtered_df.loc[mask_hot, 'Island or seamount'].unique())
        group_keys = sorted(islands, key=lambda x: (x == 'Nicht angegeben', x))
        def make_mask(g):
            if g == 'Nicht angegeben':
                return mask_hot & filtered_df['Island or seamount'].isna()
            return mask_hot & (filtered_df['Island or seamount'].astype(str) == g)
    else:
        if 'All Islands' not in selected_islands:
            group_keys = list(selected_islands)
            def make_mask(g):
                return filtered_df['Island or seamount'].isna() if g == 'Nicht angegeben' else (filtered_df['Island or seamount'].astype(str) == g)
        else:
            islands = labelize(filtered_df['Island or seamount'].unique())
            group_keys = sorted(islands, key=lambda x: (x == 'Nicht angegeben', x))
            def make_mask(g):
                return filtered_df['Island or seamount'].isna() if g == 'Nicht angegeben' else (filtered_df['Island or seamount'].astype(str) == g)

    n_colors = max(1, len(group_keys))
    palette = sns.color_palette("husl", n_colors=n_colors)

    plotted_any = False
    for i, key in enumerate(group_keys):
        mask = make_mask(key)
        mask_idx = mask & valid_all
        if not mask_idx.any():
            continue
        x_vals = x_ratio_full[mask_idx].to_numpy()
        y_vals = y_ratio_full[mask_idx].to_numpy()
        # If log scale is set, only plot positive non-zero values
        if x_log:
            x_vals = x_vals[x_vals > 0]
        if y_log:
            y_vals = y_vals[y_vals > 0]
        if x_vals.size == 0 or y_vals.size == 0:
            continue
        plotted_any = True
        ax.scatter(x_vals, y_vals,
                   color=palette[i % len(palette)], label=str(key),
                   alpha=1, zorder=2, edgecolors='black', s=40)

    ax.set_xlabel(f'{x1} / {x2}')
    ax.set_ylabel(f'{y1} / {y2}')
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    if x_log:
        ax.set_xscale('log')
    if y_log:
        ax.set_yscale('log')
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.65), ncol=4)
    #fig.tight_layout()

    st.pyplot(fig)

    # PDF Download Button
    buf = io.BytesIO()
    fig.savefig(buf, format="pdf", bbox_inches='tight', dpi=300, pad_inches=0.5)
    buf.seek(0)
    st.download_button(
        label="Download Plot as PDF",
        data=buf,
        file_name="OIB_plot.pdf",
        mime="application/pdf"
    )

if __name__ == "__main__":
    main()
