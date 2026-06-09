import streamlit as st
import pandas as pd
import math
from pathlib import Path

from annabanai import AnnabanRuntime, RuntimeConfig

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='GDP dashboard',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - Country Name
    # - Country Code
    # - Year
    # - GDP
    #
    # So let's pivot all those year-columns into two: Year and GDP
    gdp_df = raw_gdp_df.melt(
        ['Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )

    # Convert years from string to integers
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])

    return gdp_df

gdp_df = get_gdp_data()
BOOTSTRAP_SCRIPT = (Path(__file__).parent / 'annabanai_bootstrap_colab.txt').read_text()
RUNTIME_DB = Path(__file__).parent / 'annabanai_outputs' / 'runtime_state.db'
RUNTIME_AUDIT = Path(__file__).parent / 'annabanai_outputs' / 'interactions.jsonl'
ARCHITECTURE_NOTES = """
AnnabanAI Review Directive:
- Unify memory: make SQLite the source of truth; JSON as audit mirror.
- Stabilize inference: add provider abstraction (OpenAI/xAI/fallback).
- Add orchestration: central runtime class with deterministic logging flow.
- Fuse sentiment: weighted DistilBERT + TextBlob signal.
"""


@st.cache_resource
def get_annaban_runtime():
    """Initialize the AnnabanAI runtime once per Streamlit session."""
    return AnnabanRuntime(
        RuntimeConfig(
            db_path=str(RUNTIME_DB),
            audit_path=str(RUNTIME_AUDIT),
            preferred_provider='fallback',
            fallback_provider='fallback',
        )
    )

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_americas: GDP dashboard

Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
But it's otherwise a great (and did I mention _free_?) source of data.
'''

# Add some spacing
''
''

min_value = gdp_df['Year'].min()
max_value = gdp_df['Year'].max()

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

countries = gdp_df['Country Code'].unique()

if not len(countries):
    st.warning("Select at least one country")

selected_countries = st.multiselect(
    'Which countries would you like to view?',
    countries,
    ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'])

''
''
''

# Filter the data
filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries))
    & (gdp_df['Year'] <= to_year)
    & (from_year <= gdp_df['Year'])
]

st.header('GDP over time', divider='gray')

''

st.line_chart(
    filtered_gdp_df,
    x='Year',
    y='GDP',
    color='Country Code',
)

''
''


first_year = gdp_df[gdp_df['Year'] == from_year]
last_year = gdp_df[gdp_df['Year'] == to_year]

st.header(f'GDP in {to_year}', divider='gray')

''

cols = st.columns(4)

for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]

    with col:
        first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
        last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000

        if math.isnan(first_gdp):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_gdp / first_gdp:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{country} GDP',
            value=f'{last_gdp:,.0f}B',
            delta=growth,
            delta_color=delta_color
        )

st.header('AnnabanAI orchestration console', divider='gray')
runtime = get_annaban_runtime()
console_tab, monitor_tab, events_tab, memory_tab = st.tabs([
    'Prompt workspace',
    'Runtime monitor',
    'Event viewer',
    'Memory inspection',
])

with console_tab:
    with st.container(border=True):
        st.subheader('Task execution panel')
        user_prompt = st.text_area(
            'Send a prompt through AnnabanRuntime',
            placeholder='Ask AnnabanAI to plan, review, execute, or audit a task…',
            key='annabanai_runtime_prompt',
        )
        provider_choice = st.selectbox('Provider route', ['fallback', 'openai', 'xai'], index=0)
        if st.button('Run orchestration', type='primary') and user_prompt:
            result = runtime.process_input(
                user_prompt,
                user_id='streamlit_user',
                provider_name=provider_choice,
                metadata={'surface': 'streamlit'},
            )
            st.session_state['last_runtime_result'] = result
        if 'last_runtime_result' in st.session_state:
            result = st.session_state['last_runtime_result']
            st.markdown('**Runtime response**')
            st.write(result.response)
            st.caption(f'Correlation ID: {result.correlation_id}')
            st.json({
                'sentiment': result.sentiment.__dict__,
                'provider': result.provider_response.__dict__,
            })

with monitor_tab:
    health = runtime.health()
    st.subheader('Runtime health')
    st.json(health)

with events_tab:
    st.subheader('Deterministic event replay')
    st.dataframe(runtime.memory_manager.replay_events()[-50:], use_container_width=True)

with memory_tab:
    st.subheader('SQLite source-of-truth interactions')
    st.dataframe(runtime.memory_manager.recent_interactions(limit=20), use_container_width=True)

st.header('Illustration boxes', divider='gray')
st.caption('Use these boxed sections to sketch ideas like a ChatGPT-style canvas.')
with st.container(border=True):
    st.subheader('Canvas boot script')
    st.text_area(
        'Colab bootstrap code',
        value=BOOTSTRAP_SCRIPT,
        height=360,
        key='canvas_boot_script',
    )
    st.download_button(
        'Download bootstrap script',
        data=BOOTSTRAP_SCRIPT,
        file_name='annabanai_bootstrap_colab.txt',
        mime='text/plain',
    )

with st.container(border=True):
    st.subheader('AnnabanAI architecture review')
    st.text_area(
        'Structured handoff notes',
        value=ARCHITECTURE_NOTES.strip(),
        height=170,
        key='architecture_review_notes',
    )

box_count = st.slider('Number of illustration boxes', min_value=1, max_value=6, value=3)

for box_number in range(1, box_count + 1):
    with st.container(border=True):
        st.subheader(f'Illustration box {box_number}')
        prompt_text = st.text_area(
            f'Illustration prompt {box_number}',
            placeholder='Describe what you want to illustrate…',
            key=f'illustration_prompt_{box_number}',
        )
        st.markdown(prompt_text if prompt_text else '_Your illustration notes will appear here._')
