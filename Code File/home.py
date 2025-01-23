import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

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
    else:
        if (
            list_[i][1] == " "
            or list_[i][1] == ""
            or list_[i][1] == "n/a"
            or list_[i][1] == ","
        ):  # removing invalid
            # entries
            state.append("other")
        else:
            state.append(list_[i][1].lower())

        if len(list_[i]) < 3:
            country.append("other")
        else:
            if (
                list_[i][2] == ""
                or list_[i][1] == ","
                or list_[i][2] == " "
                or list_[i][2] == "n/a"
            ):
                country.append("other")
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


# Function for getting most popular recommendations
def most_popular(df, books_df, n):
    if n >= 1 and n <= len(df):
        popular = (
            df.groupby("ISBN")["Book-Rating"]
            .count()
            .reset_index()
            .sort_values(by="Book-Rating", ascending=False)
            .head(n)
        )
        popular_books = pd.merge(popular, books_df, on="ISBN")
        return popular_books
    return pd.DataFrame()


# Streamlit UI
def main():
    st.title("Book Recommendation System")
    st.sidebar.title("Options")
    option = st.sidebar.selectbox(
        "Select an Option",
        [
            "Books Data",
            "Users Data",
            "Ratings Data",
            "Merge Data",
            "Most Popular Rating",
            "Top 5 Most Popular Books",
            "Most Popular Authors",
            "Age Distribution of Users",
            "Books by Author",
            "Books by Publisher",
            "Readers by Country",
            "Readers by State",
            "Readers by City",
            "Popular Book Recommendations",
        ],
    )

    if option == "Books Data":
        # Displaying shapes of datasets
        st.subheader("Shape of Books Dataset")
        st.write(books_df.shape)

        # Displaying info of Books DataFrame
        st.subheader("Info of Books Dataset")
        st.write(books_df.info())

        # Displaying descriptive statistics of Books DataFrame
        st.subheader("Descriptive Statistics of Books Dataset")
        st.write(books_df.describe())

        # Displaying missing value percentage in Books DataFrame
        st.subheader("Missing Value Percentage in Books Dataset")
        st.write(books_df.isnull().sum() / len(books_df) * 100)

        # Displaying cleaned Books DataFrame
        st.subheader("Cleaned Books Dataset")
        st.write(books_df)

    elif option == "Users Data":
        # Displaying shapes of datasets
        st.subheader("Shape of Users Dataset")
        st.write(users_df.shape)

        # Displaying info of Users DataFrame
        st.subheader("Info of Users Dataset")
        st.write(users_df.info())

        # Displaying top and bottom rows of Users DataFrame
        st.subheader("Top and Bottom Rows of Users Dataset")
        st.write(pd.concat([users_df.head(10), users_df.tail(10)], axis=0))

        # Checking for duplicates in 'User-ID' column
        st.subheader("Checking for Duplicates in 'User-ID' Column")
        duplicates = users_df[users_df["User-ID"].duplicated()]
        if len(duplicates) > 0:
            st.write("Duplicate 'User-ID' found.")
            st.write(duplicates)
        else:
            st.write("No duplicate 'User-ID' found.")

        # Summarizing data in 'Age' column
        st.subheader("Summary of 'Age' Column")
        st.write(users_df["Age"].describe())

        # Histogram showing distribution of ages
        st.subheader("Histogram of 'Age' Column")
        plt.figure(figsize=(12, 6))
        sns.histplot(x="Age", data=users_df)
        plt.title("Age Distribution of Users")
        st.pyplot()

        # Boxplot of 'Age' column
        st.subheader("Boxplot of 'Age' Column")
        plt.figure(figsize=(12, 6))
        sns.boxplot(x="Age", data=users_df)
        plt.title("Age Distribution of Users")
        st.pyplot()

    elif option == "Ratings Data":
        # Displaying first 5 rows of Ratings DataFrame
        st.subheader("First 5 Rows of Ratings Data")
        st.write(rating_df.head())

        # Displaying info of Ratings DataFrame
        st.subheader("Info of Ratings Data")
        st.write(rating_df.info())

        # Checking for null values
        st.subheader("Checking for Null Values")
        st.write(rating_df.isna().sum())

        # Checking for unique User-IDs and ISBNs
        st.subheader("Unique User-IDs and ISBNs")
        st.write("Number of unique User-IDs:", rating_df["User-ID"].nunique())
        st.write("Number of unique ISBNs:", rating_df["ISBN"].nunique())

        # Converting ISBNs to uppercase
        rating_df["ISBN"] = rating_df["ISBN"].str.upper()

        # Checking for duplicates
        st.subheader("Checking for Duplicates")
        duplicates = rating_df[rating_df.duplicated()]
        if not duplicates.empty:
            st.write("Duplicate entries found:")
            st.write(duplicates)
        else:
            st.write("No duplicates found.")

    elif option == "Merge Data":
        # Merging Datasets
        df = pd.merge(
            books_df, rating_df[rating_df["Book-Rating"] != 0], on="ISBN", how="inner"
        )
        df = pd.merge(df, users_df, on="User-ID", how="inner")

        # Displaying shape of merged dataframe
        st.subheader("Shape of Merged DataFrame")
        st.write(df.shape)

        # Displaying top 8 rows of merged dataframe
        st.subheader("Top 8 Rows of Merged DataFrame")
        st.write(df.head(8))

        # Displaying info of merged dataframe
        st.subheader("Info of Merged DataFrame")
        st.write(df.info())

    elif option == "Most Popular Rating":
        explicit_rating = rating_df[rating_df["Book-Rating"] != 0]

        df = pd.merge(books_df, explicit_rating, on="ISBN", how="inner")
        df = pd.merge(df, users_df, on="User-ID", how="inner")
        # most popular rating
        plt.figure(figsize=[8, 5])
        plt.rc("font", size=12)
        plt.title("\nMost popular ratings\n")
        sns.countplot(data=df, x="Book-Rating", palette="Set2")
        st.pyplot()

    elif option == "Top 5 Most Popular Books":
        # top 5 most popular books
        explicit_rating = rating_df[rating_df["Book-Rating"] != 0]

        df = pd.merge(books_df, explicit_rating, on="ISBN", how="inner")
        df = pd.merge(df, users_df, on="User-ID", how="inner")
        popular = (
            df.groupby("Book-Title")["Book-Rating"]
            .count()
            .reset_index()
            .sort_values(by="Book-Rating", ascending=False)[:5]
        )
        popular.columns = ["Book-Title", "Count"]
        plt.figure(figsize=[8, 5])
        plt.rc("font", size=12)
        plt.title("\nMost popular books\n")
        sns.barplot(data=popular, y="Book-Title", x="Count", palette="Set2")
        st.pyplot()

    elif option == "Most Popular Authors":
        # most popular book authors
        explicit_rating = rating_df[rating_df["Book-Rating"] != 0]

        df = pd.merge(books_df, explicit_rating, on="ISBN", how="inner")
        df = pd.merge(df, users_df, on="User-ID", how="inner")
        author = df["Book-Author"].value_counts().reset_index()[:10]
        author.columns = ["Book-Author", "Book Count"]
        plt.figure(figsize=[8, 5])
        plt.rc("font", size=12)
        plt.title("\nMost popular Authors\n")
        sns.barplot(data=author, y="Book-Author", x="Book Count", palette="Set2")
        st.pyplot()

    elif option == "Age Distribution of Users":
        # Age distribution of users
        explicit_rating = rating_df[rating_df["Book-Rating"] != 0]

        df = pd.merge(books_df, explicit_rating, on="ISBN", how="inner")
        df = pd.merge(df, users_df, on="User-ID", how="inner")
        age_df = users_df[users_df["User-ID"].isin(list(df["User-ID"].unique()))]
        plt.figure(figsize=(12, 6))
        sns.histplot(x="Age", data=age_df)
        plt.title("Age Distribution of Users")
        st.pyplot()

    elif option == "Books by Author":
        # Books by Author
        st.subheader("Books by Author")
        books_by_author = books_df["Book-Author"].value_counts().reset_index()
        books_by_author.columns = ["Author", "Book Count"]
        st.write(books_by_author)

    elif option == "Books by Publisher":
        # Books by Publisher
        st.subheader("Books by Publisher")
        books_by_publisher = books_df["Publisher"].value_counts().reset_index()
        books_by_publisher.columns = ["Publisher", "Book Count"]
        st.write(books_by_publisher)

    elif option == "Readers by Country":
        # Readers by Country
        st.subheader("Readers by Country")
        readers_by_country = users_df["Country"].value_counts().reset_index()
        readers_by_country.columns = ["Country", "Reader Count"]
        st.write(readers_by_country.head(10))

    elif option == "Readers by State":
        # Readers by State
        st.subheader("Readers by State")
        readers_by_state = users_df["State"].value_counts().reset_index()
        readers_by_state.columns = ["State", "Reader Count"]
        st.write(readers_by_state.head(15))

    elif option == "Readers by City":
        # Readers by City
        st.subheader("Readers by City")
        readers_by_city = users_df["City"].value_counts().reset_index()
        readers_by_city.columns = ["City", "Reader Count"]
        st.write(readers_by_city.head(15))

    elif option == "Popular Book Recommendations":
        n = st.sidebar.number_input(
            "Enter the number of popular books you want to retrieve:",
            min_value=1,
            max_value=10,
            value=3,
            step=1,
        )
        if st.sidebar.button("Get Recommendations"):
            st.subheader("Recommended Books")
            explicit_rating = rating_df[rating_df["Book-Rating"] != 0]

            # Merging Datasets
            df = pd.merge(books_df, explicit_rating, on="ISBN", how="inner")
            df = pd.merge(df, users_df, on="User-ID", how="inner")
            popular_books = most_popular(df, books_df, n)
            if not popular_books.empty:
                st.markdown('<div class="books-container">', unsafe_allow_html=True)
                for index, row in popular_books.iterrows():
                    st.markdown('<div class="book">', unsafe_allow_html=True)
                    # Display the book image
                    try:
                        st.markdown(
                            f'<img class="book-image" src="{row["Image-URL-M"]}" alt="{row["Book-Title"]}">',
                            unsafe_allow_html=True,
                        )
                    except Exception as e:
                        st.write(
                            f"Error loading image for book: {row['Book-Title']}. Error: {e}"
                        )
                    # Display the book details
                    st.markdown('<div class="book-details">', unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="book-title">{row["Book-Title"]}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div class="book-info">ISBN: {row["ISBN"]}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div class="book-info">Author: {row["Book-Author"]}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div class="book-info">Year of Publication: {row["Year-Of-Publication"]}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.write("No popular books found.")


if __name__ == "__main__":
    main()
