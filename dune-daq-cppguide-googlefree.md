
# JCF, Mar-17-2020: If you edit this file, remember to also edit dune-daq-cppguide.md 

# C++ Style Guide (based on Google's C++ Style Guide)

###### tags: `Software Management` `DAQ` `DUNE`

## Background

C++ is the main development language of DUNE's DAQ software
processes. It is an unusually complex language, which can make code
more bug-prone and harder to read and maintain.

The goal of this guide is to manage this complexity by describing in
detail the dos and don'ts of writing C++ code. These rules exist to
keep the code base manageable while still allowing coders to use C++
language features productively. While it will take a certain amount of
time to learn these rules and adhering to them may mean that creating
a piece of code that "just works" would take a little longer than it
otherwise would, the payoff in terms of reduced debugging time and
increased readability will be well worth it.

Note that this guide is not a C++ tutorial: we assume that the reader is
familiar with the language.

## C++ Version

Currently, code should target C++17, i.e., should not use C++2x
features.

## Header Files 

Header files should have an `.hh` extension. They fall into one of two
categories: public header files (those meant to be included by code
using a library) and private header files (those only included by
library implementation files). Public header files shall be placed in
the `include/package_name` directory (where `package_name` is a
stand-in for the name of the package). Private headers are kept with
source files under the `src/` directory.

In general, every `.cc` file should have an associated `.hh` file. There
are some common exceptions, such as unittests and small `.cc` files
containing just a `main()` function.

### Self-contained Headers

Header files should be self-contained (compile on their own) and end in
`.hh`. Non-header files that are meant for inclusion should end in `.inc`
and be used very rarely. 

All header files should be self-contained. Users and refactoring tools
should not have to adhere to special conditions to include the header.
Specifically, a header should have [header guards](#The__define_Guard)
and include all other headers it needs.

Prefer placing the definitions for template and inline functions in the
same file as their declarations. The definitions of these constructs
must be included into every `.cc` file that uses them, or the program
may fail to link in some build configurations. If declarations and
definitions are in different files, including the former should
transitively include the latter. 

As an exception, a template that is explicitly instantiated for all
relevant sets of template arguments, or that is a private implementation
detail of a class, is allowed to be defined in the one and only `.cc`
file that instantiates the template.


### The \#define Guard 

All header files should have `#define` guards to prevent multiple
inclusion. The format of the symbol name should be
`<PROJECT>_<PATH>_<FILE>_H_`.


### Inline Functions

Define functions inline only when they are small, say, 10 lines or
fewer. Feel free to inline accessors and mutators, and other short,
performance-critical functions. Don't inline functions with loops or
switch statements (unless, in the common case, the loop or switch
statement is never executed).


### Names and Order of Includes 

If the included header is the "related header" - meaning, you're editing foo.cc 
and the header is foo.hh - put it before all the other headers.

Then, in order:

 - private headers
 - public headers from current package
 - public headers from other packages in project
 - public headers from external dependencies
 - standard library headers

All of a project's header files should be listed as descendants of the
project's source directory without use of UNIX directory aliases `.`
(the current directory) or `..` (the parent directory). For example,
`google-awesome-project/src/base/logging.h` should be included as:

```c++
#include "base/logging.h"
```

You should include all the headers that define the symbols you rely
upon, except in the unusual [?] case of [forward
declaration](#Forward_Declarations). Note that the order of header
declarations described above helps enforce this rule. If you rely on
symbols from `bar.h`, don't count on the fact that you included
`foo.h` which (currently) includes `bar.h`: include `bar.h` yourself,
unless `foo.h` explicitly demonstrates its intent to provide you the
symbols of `bar.h`.



## Scoping

### Namespaces

With few exceptions, place code in a namespace. As of this writing, Mar-17-2020, there aren't yet a standard set of namespaces for DUNE DAQ software, but this may well change. Avoid using *using-directives* (e.g. `using namespace foo`) in header files, as any files which include them may risk name collisions and, worse, unexpected behavior when the "wrong" function/class is picked up by the compiler. They're less damaging when employed in source files and can reduce code clutter, but make sure to only use them *after* including all your headers, and be aware of their risks. 

Also in the vein of reducing code clutter, using-declarations (e.g., `using heavily::nested:namespace::foo::FooClass` can be useful for improving readability. For unnamed namespaces, see [Unnamed Namespaces and Static
Variables](#Unnamed_Namespaces_and_Static_Variables).

When creating nonmember functions which work with a class, keep in mind that these functions are part of the class's interface and therefore should be in the same namespace as the class.

Namespaces should be used as follows:

  - Follow the rules on [Namespace Names](#Namespace_Names).

  - Terminate namespaces with comments as shown in the given examples.

  - Namespaces wrap the entire source file after includes,
    definitions/declarations
    and forward declarations of classes from other namespaces.
    
 ```c++
     // In the .hh file
     namespace mynamespace {
     
        // All declarations are within the namespace scope.
        // Notice the indentation of four spaces

        class MyClass {
           public:
               ...
               void Foo();
        };
     
     }  // namespace mynamespace
 
     // In the .cc file
     namespace mynamespace {
     
         // Definition of functions is within scope of the namespace.
         void MyClass::Foo() {
             ...
         }
     
     }  // namespace mynamespace
```
[Are people happy with the indentations above?]

More complex `.cc` files might have additional details, like using-declarations.
  
``` c++
    #include "a.hh"
    
    namespace mynamespace {
    
        using ::foo::Bar;
    
        ...code for mynamespace... 
    
    }  // namespace mynamespace
```


  - Do not declare anything in namespace `std`, including forward
    declarations of standard library classes. Declaring entities in
    namespace `std` is undefined behavior, i.e., not portable. To
    declare entities from the standard library, include the appropriate
    header file.
   

  - Do not use *Namespace aliases* at namespace scope in header files
    except in explicitly marked internal-only namespaces, because
    anything imported into a namespace in a header file becomes part of
    the public API exported by that file.
    
  ``` c++  
        // Shorten access to some commonly used names in .cc files.
        namespace baz = ::foo::bar::baz;
    
        // Shorten access to some commonly used names (in a .h file).
        namespace librarian {
            namespace impl {  // Internal, not part of the API.
            namespace sidetable = ::pipeline_diagnostics::sidetable;
        }  // namespace impl
        
        inline void my_inline_function() {
            // namespace alias local to a function (or method).
            namespace baz = ::foo::bar::baz;
            ...
        }
        }  // namespace librarian
 ```


### Unnamed Namespaces and Static Variables

When definitions in a `.cc` file do not need to be referenced outside
that file, place them in an unnamed namespace or declare them `static`.
Do not use either of these constructs in `.hh` files.

Format unnamed namespaces like named namespaces. In the terminating
comment, leave the namespace name empty:

```c++
    namespace {
        ...
    }  // namespace
```

### Nonmember, Static Member, and Global Functions

 - Use completely global functions rarely, and only if there's a compelling reason

 - If a nonmember function can accomplish what a member function can, prefer a nonmember function. This is because the less code a class's data is exposed to, the less opportunity there is for bugs.

 - Nonmember functions should always be in a namespace, and unless there's a compelling reason to violate this rule, to go in the same namespace as the class it works with

 - Static methods of a class should generally be closely related to
instances of the class or the class's static data.

### Local Variables

Declare local variables in as local a scope as possible, and as close to the
first use as possible. Always initialize variables in the declaration.

There is one caveat: if the variable is an object, its constructor is
invoked every time it enters scope and is created, and its destructor is
invoked every time it goes out of scope.

``` c++
// Inefficient implementation:
for (int i = 0; i < 1000000; ++i) {
    Foo f;  // My ctor and dtor get called 1000000 times each.
    f.DoSomething(i);
}
```

For pointer variables, this would translate to initializing the pointer to nullptr:
``` c++
std::unique_ptr fptr = nullptr;
if (able_to_read_data) {
    fptr = new Foo();
    // fill the Foo instance with the data
}
if (fptr != nullptr) {
    // send data
}
```

### Static and Global Variables 

The less complex the constructors and destructors of classes that 
are used as static and global variables anywhere in the code, the better.
In particular, keep in mind there's no
guarantee on the order of construction of these variables, and hence
code should never rely on an assumed order.

## Classes


### Doing Work in Constructors 

 - Don't call any of a class's virtual functions in its constructor.  This will not result in the correct invokation of subclass implementatiosn of those virtual functions.

 - If an error occurs that will prevent the class from being constructed, have it throw an exception. As its destructor won't execute in this scenario, make sure you clean up any resources the constructor allocated before throwing.

 - Initialize a class's member in the constructor's member initialization list rather than assign to it in the constructor's body. An exception to this might be if the member class's default constructor is much faster than its other constructors/assignment operator, but it's not guaranteed that it'll even need to be assigned to. 


### Implicit Conversions

In general, use the `explicit` keyword in the declaration of constructors
to avoid having them used to perform an implicit conversion in user code.
Type conversion
operators, and constructors that are callable with a single argument,
should be marked `explicit` in the class definition. As an exception,
copy and move constructors should not be `explicit`, since they do not
perform type conversion. Also, implicit conversions can sometimes be
necessary and appropriate for types that are designed to transparently
wrap other types; in this case an exception to the rule is allowed.

Constructors that cannot be called with a single argument may omit
`explicit` since the C++ language does not consider multi-argument
constructors for implicit conversions.

### Copyable and Movable Types 

If a class contains member data, its copy constructor, copy
 assignment operator, move constructor and move assignment operators
 must all be either defined or explicitly deleted. "Defined" could be
 as simple as making explicit the use of the "default" keyword.

### Structs vs. Classes

Always use a `class` rather than `struct` unless you're creating:

 - A passive object only meant to carry data
 - A small callable with an `operator()` defined

If using a struct to carry data, all fields must be public, and accessed directly rather than
through getter/setter methods. Any functions must not provide behavior
but should only be used to set up the data members, e.g., constructor,
destructor, `Initialize()`, `Reset()`.

Note that member variables in structs and classes have [different naming
rules](#Variable_Names).


### Structs vs. Pairs and Tuples 

Prefer to use a `struct` instead of a pair or a tuple whenever the
elements can have meaningful names.

Exception: Pairs and tuples may be appropriate in generic code where
there are not specific meanings for the elements of the pair or
tuple. Their use may also be required in order to interoperate with
existing code or APIs.


<span id="Multiple_Inheritance"></span>

### Inheritance

When class B inherits from class A, it should almost always be public
inheritance ("inheritance of interface"). Protected and private
inheritance is known as "inheritance of implementation" and results in
less encapsulation than, say, having class B contain a member of class
A and use its functionality ("composition"). Multiple inheritance of implementation is *especially* bad. 

Explicitly annotate overrides of virtual functions or virtual
destructors with exactly one of an `override` or `final` specifier. 

### Operator Overloading

There's a limited set of circumstances in which it's OK to overload operators:

 - For copying, operator=. More in the section on [copy constructors](#Copy_Constructors).
 - For type conversions, operator(). More in [implicit conversions](#Implicit_Conversions).
 - When defining comparison operators for a user-defined type
 - Outputting a type's value where it makes sense, by streaming with operator<<. Overloading `<<` for use with streams is covered in the section on [streams](#Streams).

### Access Control

In the interests of encapsulation, keep the access level of a class's
member functions only as generous as necessary. I.e., prefer private
functions over protected functions, protected functions over public
functions. Of course, use common sense: if you're writing an abstract
base class, your functions will be public!

In a class, never declare data as protected or public. Use accessor
functions if you must. 


### Declaration Order

A class definition should start with a `public:` section,
followed by `protected:`, then `private:`. Omit sections that would be
empty.

Within each section, generally prefer grouping similar kinds of
declarations together, and generally prefer the following order: 

 - types (including `typedef`, `using`, and nested structs and classes)
 - constants 
 - constructors
 - assignment operators
 - destructor
 - all other methods
 - data members.

Do not put large method definitions inline in the class definition. See [Inline Functions](#Inline_Functions) for
more details.


## Functions

### General guidelines for writing a function [DUNE VERSION of nonexistent section]

 - Have it do one thing, rather than many things (the "Swiss army knife" trap)
 - If it starts getting long (say, beyond 40 lines) think about ways it could be broken up into other functions
 - Prefer names that describe, to an appropriate level of precision, what the function does

### Output Parameters

If your function creates a single value and you don't anticipate it ever
needing to return more than a single value, have it return
it. Otherwise, use pass-by-reference in the argument list. These
output arguments should appear after the input arguments. Parameters
which serve both as input *and* output should be placed in-between.

### Function Overloading

If a function is overloaded by the argument types alone, make sure its
behavior is very similar across the types, especially if the types are
themselves similar (e.g., std::string vs. const char*).

If the behavior is noticeably different, prefer different function names.

### Default Arguments

Default arguments are allowed on non-virtual functions when the
default is guaranteed to always have the same value. Always define the
value of the argument in the header, as it's part of the function's
interface.

[KB, March 23, 2020: it would be great to talk about special situations
in which a default argument could be supported in subclasses.]

### Trailing Return Type Syntax

The only time it's OK to use a trailing return type (when the return type is 
listed after the function name and the argument list in the declaration; C++11)
is when specifying
the return type of a [lambda expression](#Lambda_expressions). In some
cases the compiler is able to deduce a lambda's return type, but not
in all cases.

### Ownership and Smart Pointers

 - You should find yourself using std::unique_ptr more often than std::shared_ptr

 - Use of raw pointers should be very rare. One of the few times it's OK is when you want to point to an object where you don't want to change anything about its ownership. Even there, a std::weak_ptr is preferable. 

 - A corollary is that you should (almost) never use delete on a raw pointer because we expect that the use of raw pointers in DUNE DAQ will be limited to low-overhead access to pre-existing memory buffers, in which the user does not have ownership of the memory that is pointed to.

## Other C++ Features

### Rvalue References

Use rvalue references to:

  - Define move constructors and move assignment operators. You should
    always have these defined when you've created a new type and
    there's the possibility that its copy operations may be
    significantly slower.

  - Support perfect forwarding in generic code

  - Define pairs of overloads, one taking `Foo&&` and the other taking
`const Foo&`, when this might improve performance

### Friends

Use friend classes only when alternatives result in less
encapsulation. An example of this would be if there's only one
nonmember function which you could imagine would ever need a given
member of a class - in this case, while you could make that given
member public, it would result in less encapsulation than use of a
friend function.

Define your friend function in the same file as the class it's a friend of. 

### Exceptions

Throw an exception if your code's encountered a problem it can't
recover from on its own. Don't throw if you can implement a local
recovery, and definitely don't throw exceptions as form of flow
control when there's not an unexpected problem. 
 
Before you throw an exception, try to clean up as much as possible -
release resources, etc. RAII is your friend here. 

Like the parameters a function takes and a function's return value,
the types of exception a function throws are part of the interface it
presents to the caller. For this reason, think carefully when adding
an exception throw to a function other callers are already using. Will
they be able to handle the new exception? If not, can they at least
release resources correctly?

Never throw exceptions out of a destructor

Only use catch(...) directly inside of main(), and then only to clean up
resources before terminating the program

Catch by const reference

When you catch, print as much info about the exception as would be
useful to users of the program

[Rules about which types of exception to use? Are there DUNE-specific
exceptions we should define since Boost/STL doesn't cover our needs,
or would that be an unnecessary vanity project?]



### `noexcept`

If you've designed a type, strive to make its move and copy functions
noexcept. This is because compilers can perform optimizations when it
comes to STL functionality if noexcept is specified. 

Otherwise, use noexcept judiciously. Keep in mind you can't take it
back later, and that it's very hard to make this guarantee if you're
writing generic code. For this reason, intelligently choose your
conditionals inside of noexcept()

### Run-Time Type Information (RTTI)

The only time Run Time Type Information (RTTI) can be used is in code
meant to test other code.


### Casting


Do not use C-style casts (e.g., "(float)3.5" or "float(3.5)")

Use reinterpret_cast only for low level code, and only if you're sure
there's no safer approach

### Printing Messages

Use TRACE for output. Never use alternatives (this includes printf, cout, etc.)

Include as much information useful for debugging in warning/error
messages. E.g., rather than "Data found corrupt", go with "Data found
corrupt in data packet ID #8294 with timestamp 0x3527378 (55735160
decimal) in run 34872"

Overload `<<` for streaming only for types representing values, and write only
the user-visible value, not any implementation details.

Take care that a given print statement not swamp other the output of
other equally-or-even-more-important messages

Distinguish between print statements meant for users, and for yourself and other developers. Use TRACE levels above 0-4 for the former, and 5+ for the latter. 

[Re: TRACE levels. Perhaps we should come up with a formal system for what levels for what time of messages? E.g., benchmark messages in trace levels 10-14, intermediate variable value messages in levels 15-19, etc.]


### Preincrement and Predecrement

Use prefix form (`++i`) of the increment and decrement operators

Unless in a loop construct, a preincrement/predecrement should exist
on its own line. In particular, it should not be used in an if
statement.

### Use of const

Particularly since DUNE processes will involve many threads, intelligent use of "const" is important. 

Use "const" on variables whose values won't change now or in future
code revisions UNLESS you need to pass it to a (poorly-designed) API
which doesn't change the variable's value but doesn't declare it const
in its function signatures

If a class method alters the class instance's physical state but not its logical
state, declare it const and use "mutable" so the compiler allows the physical changes.

constexpr is even better than const; use it when you can. [reference to constexpr section]

[where to put the const? Like Google, I prefer "const type varname" over "type const varname", but not as much as I prefer avoiding holy wars]

### Use of constexpr

If a variable or function's return value is fixed at compile time and
you don't see this ever changing, declare it constexpr.  I say "don't
see this ever changing" since similar to "const" or "noexcept", changing this later will likely break other people's code.


### Integer Types

Unless you have a good reason not to, use "int". An obvious good
reason would be that you need 64 bits to represent a value, e.g., a timestamp. Another would be that the variable represents a discrete quantity, in which case size_t would clarify its semantics. 

When you want a specific size in bytes, don't use C integer types
besides "int": no "short", "long", etc. Use "intN_t", N being the
number of bits.

You should not use the unsigned integer types such as `uint32_t`, unless
there is a valid reason such as representing a bit pattern rather than a
number, or you need defined overflow modulo 2^N. In particular, do not
use unsigned types to say a number will never be negative. Instead, use
assertions for this.

If your code is a container that returns a size, be sure to use a type
that will accommodate any possible usage of your container. When in
doubt, use a larger type rather than a smaller type.

Use care when converting integer types. Integer conversions and
promotions can cause undefined behavior, leading to security bugs and
other problems.

Code should be 64-bit friendly. [does it need to be 32-bit friendly?]


### Preprocessor Macros 

While not explicitly forbidden, macros come with the very heavy price of the code you see not being the code the compiler sees, a problem compounded by their de-facto global scope. Avoid them if at all possible, using inline functions,
enums, `const` variables, and putting repeated code inside of functions. 

If you *must* write a macro, this will avoid many of their problems:

  - Don't define macros in a header file.
  - `#define` macros right before you use them, and `#undef` them right
    after.
  - Do not just `#undef` an existing macro before replacing it with your
    own; instead, pick a name that's likely to be unique.
  - Try not to use macros that expand to unbalanced C++ constructs, or
    at least document that behavior well.
  - Have the variable names in your macro be very unlikely to be used elsewhere in unrelated code
  - Prefer not using `##` to generate function/class/variable names.

### 0 and nullptr/NULL

Use `nullptr` for pointers, and `'\0'` for the null character. Don't use NULL, and definitely don't use the number "0" in this context. 

### sizeof

Prefer `sizeof(varname)` to `sizeof(type)`, unless you really do mean that you want the size of a particular type, and not a variable which happens to have the type in question. 

### Type deduction

The `auto` and `decltype` keywords save a lot of hassle for the
*writer* of a piece of code, but not necessarily for the
*reader*. Keep in mind the reader might be you in 18 months. Use your
best judgement as to when the benefits of these keywords (reduced code
clutter) outweigh the costs (the reader can't immediately figure out
the type of a variable).

While a function template can deduce the type of the argument, making
this explicit will typically make it clearer to both the code's reader
and to the compiler what it is you're trying to do.


## Comments

[This section needs to be made consistent with DOxygen standards on DUNE]

Comments are absolutely vital to keeping our code readable. But
remember: while comments are very important, the best code is
self-documenting. Give sensible names to types and variables, and
don't make code "clever" unless it creates clear performance
improvements in bottleneck regions. If it's obvious what a function
does, don't clutter the code with a comment. E.g., don't do something
like this:

```
// "sqrt" calculates the square root of a variable
double sqrt(double); 
```


### Comment Style

Use either the `//` syntax instead of the old C-style `/* */` syntax

### File Comments

Avoid license boilerplate at the top of a file. This does NOT mean you ignore licensing. Instead, have something succinct like:
```
 // This is part of XXX, copywrite YYY.  It is distributed under               
  // license LLL.  See the file COPYING for deatils.          
```

File comments describe the contents of a file. If a file declares,
implements, or tests exactly one abstraction that is documented by a
comment at the point of declaration, file comments are not required. All
other files must have file comments.

The comment at the top of a header file should never describe
implementation details the user of a class doesn't need to worry
about. Save those either for the source file, or for just above the
definition of an inline function if it's in the header file.

Comments are always in danger of growing stale as code changes. This
danger is greatest when it comes to the comment at the top of the
file. Be aware of this when you modify code, and update the comments
if necessary.

#### File Contents

If a `.hh` declares multiple abstractions, the file-level comment should
broadly describe the contents of the file, and how the abstractions are
related. A 1 or 2 sentence file-level comment may be sufficient. The
detailed documentation about individual abstractions belongs with those
abstractions, not at the file level.

Do not duplicate comments in both the `.hh` and the `.cc`. Duplicated
comments diverge.


### Class Comments

Every non-obvious class declaration should have an accompanying comment
that describes what it is for and how it should be used.

The class comment should provide the reader with enough information to
know how and when to use the class, as well as any additional
considerations necessary to correctly use the class. Document the
synchronization assumptions the class makes, if any. If an instance of
the class can be accessed by multiple threads, take extra care to
document the rules and invariants surrounding multithreaded use.

### Function Comments

Declaration comments describe use of the function (when it is
non-obvious); comments at the definition of a function describe
operation.


#### Function Declarations

Function declaration should have comments immediately
preceding it that describe what the function does and how to use it *unless* the function is simple and obvious. 

Types of things to mention in comments at the function declaration:

  - What the inputs and outputs are, if not obvious
  - For class member functions: whether the object remembers reference
    arguments beyond the duration of the method call, and whether it
    will free them or not.
  - Any non-obvious preconditions and postconditions. E.g., can a
    pointer argument be null? 
  - If there are any performance implications of how a function is used.
  - If the function is re-entrant. What are its synchronization
    assumptions?

When documenting function overrides, focus on the specifics of the
override itself, rather than repeating the comment from the overridden
function. In many of these cases, the override needs no additional
documentation and thus no comment is required.

When commenting constructors and destructors, remember that the person
reading your code knows what constructors and destructors are for, so
comments that just say something like "destroys this object" are not
useful. Document what constructors do with their arguments (for example,
if they take ownership of pointers), and what cleanup the destructor
does. If this is trivial, just skip the comment. It is quite common for
destructors not to have a header comment.


#### Function Definitions

If there is anything tricky about how a function does its job, the
function definition should have an explanatory comment. For example, in
the definition comment you might describe any coding tricks you use,
give an overview of the steps you go through, or explain why you chose
to implement the function in the way you did rather than using a viable
alternative. For instance, you might mention why it must acquire a lock
for the first half of the function but why it is not needed for the
second half.

Note you should *not* just repeat the comments given with the function
declaration, in the `.h` file or wherever. It's okay to recapitulate
briefly what the function does, but the focus of the comments should be
on how it does it.

### Variable Comments

In general the actual name of the variable should be descriptive enough
to give a good idea of what the variable is used for. 

#### Class Data Members

If there are any invariants (special values, relationships between
members, lifetime requirements) not clearly expressed by the type and
name, they must be commented.

In particular, add comments to describe the existence and meaning of
sentinel values, such as nullptr or -1, when they are not obvious. 

#### Global Variables

Along with the usual rules, a global variable should have a comment as
to why it needs to be global unless it's completely clear. 

[An idea: should people have to stick some easily-searchable token,
like DUNE_GLOBAL_VAR, in the comment, so it'll be easy to find global
variables?]


### Implementation Comments

In your implementation you should have comments in tricky,
non-obvious, interesting, or important parts of your code. Of course,
tricky and non-obvious code should be avoided unless absolutely
necessary.


### Punctuation, Spelling, and Grammar

Pay attention to punctuation, spelling, and grammar; it is easier to
read well-written comments than badly written ones. In particular, a
spelling mistake can make it hard to grep for a comment in the future.

In general, comments should be in English. An exception might be if
you know the only people working on your code will be the fellow
speakers of your language, especially if they're not fluent in
English. Since this is a C++ style guide and not an English style
guide, it's understandable if English written by a non-native speaker
is less than perfect; however, don't hesitate to have a native English
speaker look over your comment if you feel it would help.

Generally, complete sentences are more readable than sentence
fragments. Shorter comments, such as comments at the end of a line of
code, can sometimes be less formal.



### TODO Comments

Use `TODO` comments for code that is temporary, a short-term solution,
or good-enough but not perfect. Date your TODO comment, and if
possible provide a time estimate (even if just something like "next
few weeks") as to when you expect something should be done.

`TODO`s should include the string `TODO` in all caps, followed by the
name, e-mail address, bug ID, or other identifier of the person or issue
with the best context about the problem referenced by the `TODO`. 

Stale TODO comments should be reviewed. If they're no longer relevant,
they should be deleted. If they're still relevant, a message should be
sent to the person whose e-mail is given in the comment. When in
doubt, send an e-mail.


## Formatting

 - Indentation should involve four spaces. Tabs should NOT be used.
 - Send your code through clang-format before committing
 - Lines should (almost) always be less than 120 characters

## Exceptions to the Rules

For new code, deviations from this guide should be quite rare. However: to the extent
that we reuse already-existing code in the DUNE DAQ codebase, the
already-existing code won't adhere to directives in this guide. If the
code is never going to be touched again, then this won't be a big
issue. If we plan on altering it in the future, it may be worth at
least getting it to be *somewhat* more conformant to the rules,
especially if the changes are relatively non-invasive (e.g., running
it through clang-format, as opposed to breaking up a long but
well-tested function). If anything about the style in existing code
may be confusing to future developers, it may be worth adding comments on
how the style deviates from the standard. 