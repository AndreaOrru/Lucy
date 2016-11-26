fib(n: Int) -> Int
{
    if (n == 0)
        return 0;

    prev: Int = 0;
    next: Int = 1;

    i: Int = 1;
    while (i < n)
    {
        sum: Int = prev + next;

        prev = next;
        next = sum;

        i = i + 1;
    }

    return next;
}

main() -> Int
{
    return fib(10);
}
