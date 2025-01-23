from typing import Union, Any

import streamlit as st
import pandas as pd
from numpy import ndarray
from pandas import Series, DataFrame
from pandas.core.generic import NDFrame
from pyarrow.lib import ExtensionArray

# Load data
book_file_path = r"C:\Users\ranau\Desktop\BOOK RECOMMENDATION SYSTEM\database\Books.csv"
books_df = pd.read_csv(book_file_path)

users_file_path = (
    r"C:\Users\ranau\Desktop\BOOK RECOMMENDATION SYSTEM\database\Users.csv"
)
users_df = pd.read_csv(users_file_path)

ratings_file_path = (
    r"C:\Users\ranau\Desktop\BOOK RECOMMENDATION SYSTEM\database\Ratings.csv"
)
rating_df = pd.read_csv(ratings_file_path)

# Split location into city, state, and country
list_ = users_df.Location.str.split(", ")

city = []
state = []
country = []
count_no_state = 0
count_no_country = 0

for i in range(0, len(list_)):
    if (
        list_[i][0] == " "
        or list_[i][0] == ""
        or list_[i][0] == "n/a"
        or list_[i][0] == ","
    ):  # removing invalid
        # entries too
        city.append("other")
    else:
        city.append(list_[i][0].lower())

    if len(list_[i]) < 2:
        state.append("other")
        country.append("other")
        count_no_state += 1
        count_no_country += 1
    else:
        if (
            list_[i][1] == " "
            or list_[i][1] == ""
            or list_[i][1] == "n/a"
            or list_[i][1] == ","
        ):  # removing invalid
            # entries
            state.append("other")
            count_no_state += 1
        else:
            state.append(list_[i][1].lower())

        if len(list_[i]) < 3:
            country.append("other")
            count_no_country += 1
        else:
            if (
                list_[i][2] == ""
                or list_[i][1] == ","
                or list_[i][2] == " "
                or list_[i][2] == "n/a"
            ):
                country.append("other")
                count_no_country += 1
            else:
                country.append(list_[i][2].lower())

users_df = users_df.drop("Location", axis=1)

temp = []
for ent in city:
    c = ent.split(
        "/"
    )  # handling cases where city/state entries from city list as state is already given
    temp.append(c[0])

df_city = pd.DataFrame(temp, columns=["City"])
df_state = pd.DataFrame(state, columns=["State"])
df_country = pd.DataFrame(country, columns=["Country"])

users_df = pd.concat([users_df, df_city, df_state, df_country], axis=1)

# Drop duplicate rows
users_df.drop_duplicates(keep="last", inplace=True)
users_df.reset_index(drop=True, inplace=True)

# Display DataFrame


# Checking for duplicates in users_df
duplicates = users_df[users_df["User-ID"].duplicated()]

explicit_rating: Union[
    Union[Series, ExtensionArray, ndarray, DataFrame, None, NDFrame], Any
] = rating_df[rating_df["Book-Rating"] != 0]

# Merging Datasets
df = pd.merge(books_df, explicit_rating, on="ISBN", how="inner")
df = pd.merge(df, users_df, on="User-ID", how="inner")
df_relevant_data = df.groupby(["Book-Title", "Book-Author"], as_index=False).agg(
    avg_rating=("Book-Rating", "mean"), ratings_count=("Book-Rating", "count")
)
v = df_relevant_data["ratings_count"]
R = df_relevant_data["avg_rating"]
C = df_relevant_data["avg_rating"].mean()
m = int(
    df_relevant_data["ratings_count"].quantile(0.90)
)  # minimum number of votes to be listed
df_relevant_data["weighted_average"] = round(((R * v) + (C * m)) / (v + m), 2)


# Function for recommending books from the same author
def author_based(book_title, number, df_relevant_data):
    author = df_relevant_data.loc[
        df_relevant_data["Book-Title"].str.lower() == book_title.lower(), "Book-Author"
    ].values
    if len(author) > 0:
        author = author[0]
        author_df = df_relevant_data.loc[
            df_relevant_data["Book-Author"] == author
        ].sort_values(by="weighted_average", ascending=False)
        st.write(f"The author of the book {book_title} is {author}\n")
        st.write(f"Here are the top {number} books from the same author\n")
        top_rec = author_df.loc[
            (author_df["Book-Title"].str.lower() != book_title.lower()),
            ["Book-Title", "weighted_average"],
        ].head(number)
        return top_rec
    else:
        return pd.DataFrame()


# Streamlit UI
def main():
    st.title("Author-based Book Recommendations")
    st.markdown(
        """
        <style>
        .reportview-container {
            background: url('https://cdn.pixabay.com/photo/2015/09/05/20/02/library-924584_960_720.jpg');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
            color: #fff;
        }
        .sidebar .sidebar-content {
            background: rgba(0, 0, 0, 0.7);
            color: #fff;
        }
        .stButton>button {
            color: #fff;
            background-color: #008CBA;
            border-color: #008CBA;
            border-radius: 5px;
        }
        .stButton>button:hover {
            background-color: #005f77;
        }
        .stTextInput>div>div>input {
            border-color: #008CBA;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Input fields for book title and number of recommendations
    book_title = st.text_input("Enter the book title:")
    number = st.number_input("Number of books to recommend:", min_value=1, step=1)

    if st.button("Get Recommendations"):
        # Call the author_based function and display recommendations
        recommendations = author_based(book_title, number, df_relevant_data)
        if not recommendations.empty:
            st.dataframe(recommendations)
        else:
            st.write("No recommendations found for the given book.")


if __name__ == "__main__":
    main()
