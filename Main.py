from Redis import connect_to_redis, vote_for_idea, submit_idea

env_path = "insert_the_path_to_the_.env_here"

def main():
    print('Welcome!')
    user_name = None
    redis_conn = connect_to_redis(env_path)

    while True:
        user_name = input('Please enter your name: ')
        if user_name.strip() != '':
            break
        print('Invalid input. Please enter your name.')

    print(f'Hello, {user_name}!')

    while True:
        print('\nMenu:')
        print('1. Submit an Idea')
        print('2. Vote for an Idea')
        print('3. Quit')

        option = input('Choose an option: ')

        if option.strip() == '1':
            success = submit_idea(redis_conn)
            if not success:
                break  # Exit the program if idea submission is canceled
        elif option.strip() == '2':
            vote_for_idea(redis_conn, user_name)
        elif option.strip() == '3':
            print('Goodbye!')
            break
        else:
            print('Invalid option. Please try again.')

if __name__ == '__main__':
    main()
