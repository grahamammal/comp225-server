# How to Download the App on Android / iOS

## How to build to iOS 🍎
https://docs.expo.io/versions/latest/expokit/expokit/

Notes:
You need an expo account
You also need XCode downloaded

make ios Bundle identifier, must be different for each team member

Analeidi's used on Ellen's expo account:
edu.macalester.assassin.analeidi

ejecting created
\\android\\
and
\\ios\\

along with changing package lock and all that junk


we'll need to install cocoapods, package manager for ios

on ios use gem install with admin
```
sudo gem install cocoapods
pod install
```

When pod install broke,

```
brew install git-lfs
git lfs install
pod update
```

At this point Analeidi's computer ran out of space


When we get it on xcode, run it on simulator

__After that works, ask paul for help getting it on actual device!!!__

## How to build to Android 🤖

1) 
While in the project directory
```
expo eject
```

then run
```
expo start
```

While this is running, open up android Studio.

__Don't update Gradle even if it says to__

Just run it on your phone
<!--stackedit_data:
eyJoaXN0b3J5IjpbODgwMDE2MzAyXX0=
-->