from resolver import DNSResolver


if __name__ == "__main__":
    resolver = DNSResolver()
    while True:
        try:
            print("Enter name: ", end='')
            name = input().strip()
            result = resolver.resolve(name)
            if result:
                if len(result) == 1:
                    print(name + " has address: ", end='')
                else:
                    print(name + " has addresses: ", end='')
                print(*result, sep='; ')
            else:
                print("Couldn't find the address, check the correctness of name.")
        except KeyboardInterrupt:
            break
